def convert_seconds_to_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if remaining_seconds > 0:
        minutes += 1
    return minutes

