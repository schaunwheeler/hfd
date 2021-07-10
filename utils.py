def clock_time_from_seconds(seconds):
    m, s = divmod(seconds, 60)
    return f'{m:02d}:{s:02d}'
