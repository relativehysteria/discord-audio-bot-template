from random import shuffle
from itertools import islice
from song import Song

class SongQueue:
    def __init__(self)
        # The song queue
        self.songs = list()

        # The voice channel this queue belongs to
        self.voice = None

    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(
                self._queue,
                item.start,
                item.stop,
                item.step)
            )
        else:
            return self._queue[item]

    def __delitem__(self, idx):
        del self.songs[idx]

    def __iter__(self):
        return self.songs.__iter__()

    def __len__(self):
        return len(self.songs)

    def clear(self):
        self.songs.clear()

    def shuffle(self):
        shuffle(self.songs)
