import datetime


def get_weekdays(date: datetime.date) -> list[datetime.date]:
    """
    Get weekdays of the week containing the specified date.

    The weekdays are returned as a list of dates, where the first element
    is Monday and the last is Friday.  If the specified date is a weekend,
    the weekdays of the next week are returned.
    """

    if date.weekday() >= 5:
        # If the date is weekend, move to the next Monday
        date += datetime.timedelta(days=(7 - date.weekday()))

    monday = date - datetime.timedelta(days=date.weekday())
    weekdays = [monday + datetime.timedelta(days=i) for i in range(5)]

    return weekdays
