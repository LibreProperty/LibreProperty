from datetime import timedelta


def count_weekend_nights(start_date, end_date):
    nights = 0
    curr_date = start_date
    while curr_date <= end_date:
        if curr_date.weekday() in [4, 5]:
            nights += 1
        curr_date += timedelta(days=1)
    return nights