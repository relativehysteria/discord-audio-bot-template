class Song:
    def __init__(self, ytdl_result: dict):
        try:
            # If we encounter an error during indexing into the result,
            # this song is simply rendered invalid..
            self.is_valid           = True
            self.title              = ytdl_result["title"]
            self.uploader           = ytdl_result["uploader"]
            self.uploader_url       = ytdl_result["uploader_url"]
            self.url                = ytdl_result["webpage_url"]
            self.duration           = ytdl_result["duration"]
            self.thumbnail          = ytdl_result["thumbnail"]
            self.stream             = get_stream_url(ytdl_result)
            self.duration_formatted = parse_duration(self.duration)
        except:
            self.is_valid           = False
