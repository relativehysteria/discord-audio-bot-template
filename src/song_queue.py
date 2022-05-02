import multiprocessing as mp
from random import shuffle
from itertools import islice
import discord


class SongQueue():
    """The song queue.

    This class doesn't use `asyncio.queue`, but rather implements its stuff
    in its own, nicely inefficient way.
    """
    def __init__(self):
        # The song queue
        self.songs = mp.Queue()

        # The voice channel this queue belongs to
        self.voice = None

        # Indicates whether the next song should be played
        self.next_song = mp.Event()

        # Currently playing song
        self.current = None

        # Whether the current song is being played on a loop
        self.loop_song = False

        # Threading for the queue and such
        self._process = mp.Process(target=self._song_player_target)
        self._process.start()


    def __del__(self):
        gLog.debug("Terminating the queue process...")
        self._process.terminate()


    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(
                self.songs.queue,
                item.start,
                item.stop,
                item.step)
            )
        else:
            return self.songs.queue[item]


    def __delitem__(self, idx):
        del self.songs.queue[idx]


    def __iter__(self):
        return self.songs.queue.__iter__()


    def __len__(self):
        return len(self.songs.queue)


    def _song_player_target(self):
        while True:
            # Change the currently playing song
            self.next_song.clear()

            # If we're not looping, wait for new songs to come up
            if not self.loop_song:
                self.current_song = self.songs.get(block=True)

            # FFMPEG options to prevent the stream from closing on lost conns
            before_options  = "-reconnect 1 -reconnect_streamed 1"
            before_options += " -reconnect_delay_max 5"

            # Play the song
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
        self.next_song.set()
