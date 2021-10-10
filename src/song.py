class Song():
    def __init__(self, ytdl_result: dict):
        try:
            # If we encounter an error during indexing into the result,
            # this song is simply rendered invalid..
            self.valid    = True
            self.uploader = ytdl_result["uploader"]
            self.url      = ytdl_result["webpage_url"]
            self.duration = ytdl_result["duration"]
            self.stream   = get_stream_url(ytdl_result)
        except:
            self.valid    = False

def get_stream_url(ytdl_result: dict):
    """Returns the first found audio stream"""
    for i in ytdl_result['formats']:
        if i['acodec'] != "none":
            return i['url']
