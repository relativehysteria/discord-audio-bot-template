from math import ceil
from youtube_dl import YoutubeDL
from log import globalLog as gLog

class Song:
    def __init__(self, ytdl_result: dict):
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

        self.stream = get_stream_url(ytdl_result)
        gLog.debug(f"Stream URL: {self.stream}")

        self.duration_formatted = parse_duration(self.duration)
        gLog.debug(f"Formatted duration: {self.duration_formatted}")


def get_song_from_query(query: str) -> Song:
    """Get the stream url from a general url."""
    query = query.strip()

    # If we don't get a link, we get a simple query
    if not query.startswith("http"):
        query = "ytsearch:" + query

    # Discord can't parse DASH manifests, i think?
    ydl_opts = {'youtube_include_dash_manifest': False}
    with YoutubeDL(ydl_opts) as ytdl:
        result = ytdl.extract_info(query, download=False)

    # Get the stream entries, that's all we care about
    if 'entries' in result:
        result = result['entries']

    gLog.debug(f"Extraction result: {result}")
    if isinstance(result, list):
        if len(result) == 0:
            return Song(dict())  # invalid Song
        result = result[0]

    return Song(result)


def get_stream_url(ytdl_result: dict) -> str:
    """Returns the first found audio stream"""
    for i in ytdl_result.get('formats'):
        if i['acodec'] != "none":
            return i['url']
    return


def parse_duration(duration: int) -> str:
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
