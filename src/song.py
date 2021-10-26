from math import ceil
from youtube_dl import YoutubeDL
from log import globalLog as gLog

class Song:
    def __init__(self, url: str):
        ytdl_result = self._get_song_from_url(url)

        self.title = ytdl_result.get("title")
        gLog.debug(f"Title: {self.title}")

        self.uploader = ytdl_result.get("uploader")
        gLog.debug(f"Uploader: {self.uploader}")

        self.uploader_url = ytdl_result.get("uploader_url")
        gLog.debug(f"Uploader URL: {self.uploader_url}")

        self.url = ytdl_result.get("webpage_url")
        gLog.debug(f"URL: {self.url}")

        self.duration = ytdl_result.get("duration")
        gLog.debug(f"Duration: {self.duration}")

        self.thumbnail = ytdl_result.get("thumbnail")
        gLog.debug(f"Thumbnail URL: {self.thumbnail}")

        self.stream = self._get_stream_url(ytdl_result)
        gLog.debug(f"Stream URL: {self.stream}")

        self.duration_formatted = self._parse_duration(self.duration)
        gLog.debug(f"Formatted duration: {self.duration_formatted}")


    def __str__(self) -> str:
        string = ""

        if self.duration_formatted:
            string += f"`[{self.duration_formatted}]` "

        if self.title:
            if self.url:
                string += f"[{self.title}]({self.url})"
            else:
                string += f"{self.title}"
        else:
            string += "[Untitled]"

        return string


    @staticmethod
    def _get_song_from_url(query: str) -> dict:
        """Get the stream url from a general url."""
        query = query.strip()

        # Discord can't parse DASH manifests, i think?
        ydl_opts = {'youtube_include_dash_manifest': False}
        with YoutubeDL(ydl_opts) as ytdl:
            try:
                result = ytdl.extract_info(query, download=False)
            except youtube_dl.DownloadError as err:
                gLog.error(f"{err}... Removing cache dir.")
                ytdl.cache.remove()

        if isinstance(result, list):
            if len(result) == 0:
                return dict()  # invalid Song
            result = result[0]

        return result


    @staticmethod
    def _get_stream_url(ytdl_result: dict) -> str:
        """Returns the first found audio stream"""
        for i in ytdl_result.get('formats'):
            if i['acodec'] != "none":
                return i['url']


    @staticmethod
    def _parse_duration(duration: int) -> str:
        """Parses the duration in seconds into a readable format"""
        if duration is None:
            return
        duration = ceil(duration)
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = ""
        if days > 0:
            duration += f"{days:02}:"
        if hours > 0 or days > 0:
            duration += f"{hours:02}:"
        duration += f"{minutes:02}:"
        duration += f"{seconds:02}"

        return duration


    @staticmethod
    def get_urls_from_query(query: str) -> [str]:
        """Returns a list of urls parsed from a query.

        Does nothing for a single-song query, but it *should* return a list of urls
        (*not* stream urls) for playlists and such.
        """
        query = query.strip()

        # If we don't get a link, we get a simple query
        if not query.startswith("http"):
            query = "ytsearch:" + query

        ydl_opts = { "extract_flat": True }
        with YoutubeDL(ydl_opts) as ytdl:
            result = ytdl.extract_info(query, download=False)

        gLog.debug(f"Extraction result: {result}")

        # Direct url to a single song
        if 'entries' not in result:
            return [query]

        urls  = []
        for entry in result['entries']:
            url = entry.get('url')
            if url is None:
                continue
            if entry.get("ie_key") == "Youtube":
                url = f"https://www.youtube.com/watch?v={url}"
            urls.append(url)

        gLog.debug(f"Parsed urls: {urls}")
        return urls
