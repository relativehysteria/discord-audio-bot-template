class Song():
    def __init__(self, ytdl_result: dict):
        try:
            # If we encounter an error during indexing into the result,
            # this song is simply rendered invalid..
            self.valid              = True
            self.title              = ytdl_result["title"]
            self.uploader           = ytdl_result["uploader"]
            self.uploader_url       = ytdl_result["uploader_url"]
            self.url                = ytdl_result["webpage_url"]
            self.duration           = ytdl_result["duration"]
            self.thumbnail          = ytdl_result["thumbnail"]
            self.stream             = get_stream_url(ytdl_result)
            self.duration_formatted = parse_duration(self.duration)
        except:
            self.valid              = False

def get_stream_url(ytdl_result: dict):
    """Returns the first found audio stream"""
    for i in ytdl_result['formats']:
        if i['acodec'] != "none":
            return i['url']


def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{} days'.format(days))
    if hours > 0:
        duration.append('{} hours'.format(hours))
    if minutes > 0:
        duration.append('{} minutes'.format(minutes))
    if seconds > 0:
        duration.append('{} seconds'.format(seconds))

    return ', '.join(duration)
