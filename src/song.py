from log import globalLog as gLog
from util import format_duration

class Song:
    def __init__(self):
        # TODO: get ytdl info
        ytdl_result = dict()

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

        # TODO: get stream url
        self.stream = ""
        gLog.debug(f"Stream URL: {self.stream}")

        self.duration_formatted = parse_duration(self.duration)
        gLog.debug(f"Formatted duration: {self.duration_formatted}")
