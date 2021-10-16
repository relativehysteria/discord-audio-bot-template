import threading
from queue import Queue
from random import shuffle
from itertools import islice

import youtube_dl
import discord

from song import Song
from log import globalLog as gLog


class SongQueue():
    """The song queue.

    This class doesn't use `asyncio.queue`, but rather implements its stuff
    in its own, nicely inefficient way.
    """
    def __init__(self):
        # The song queue
        self.songs = Queue()

        # The voice channel this queue belongs to
        self.voice = None

        # Indicates whether the next song should be played
        self.next_song = threading.Event()

        # Currently playing song
        self.current_song = None

        # Whether the currently playing song is looping
        self.loop_song = False

        # Threading for the queue and such
        self._thread      = threading.Thread(target=self._song_player_target)
        self._stop_thread = False  # Whether the thread should be destroyed
        self._thread.start()


    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(
                self.songs,
                item.start,
                item.stop,
                item.step)
            )
        else:
            return self.songs[item]


    def __delitem__(self, idx):
        del self.songs.queue[idx]


    def __iter__(self):
        return self.songs.queue.__iter__()


    def __len__(self):
        return len(self.songs.queue)


    def __del__(self):
        self._stop_thread = True
        self._thread.join()


    def clear(self):
        self.songs.queue.clear()
        self.skip()


    def shuffle(self):
        shuffle(self.songs)


    def put(self, song: Song):
        self.songs.put(song)
        gLog.debug("Added song to queue! Length: " + str(self.__len__()))


    def skip(self):
        self.loop_song = False
        if self.voice.is_playing():
            self.voice.stop()


    def pause(self):
        if self.voice.is_paused():
            self.voice.resume()
        elif self.voice.is_playing():
            self.voice.pause()


    def loop(self):
        self.loop_song = not self.loop_song


    def _song_player_target(self):
        while True:
            # Change the currently playing song
            self.next_song.clear()

            if not self.loop_song:
                # Wait for a song to appear in the queue
                self.current_song = self.songs.get(block=True)

            # FFMPEG options to prevent stream closing on lost connections
            before_options  = "-reconnect 1 -reconnect_streamed 1"
            before_options += " -reconnect_delay_max 5"

            source = discord.FFmpegPCMAudio(
                self.current_song.stream,
                before_options=before_options
            )
            self.voice.play(source, after=self._play_next_song)

            # Wait for the song to finish
            self.next_song.wait()


    def _play_next_song(self, error=None):
        if error:
            gLog.error(str(error))
            raise Exception
        self.next_song.set()
