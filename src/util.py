from math import ceil

def format_duration(duration: int) -> str:
    """Parses the duration from seconds into a readable format"""
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
