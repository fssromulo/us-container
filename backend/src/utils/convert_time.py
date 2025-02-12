# Python imports
from datetime import datetime, time, timedelta, timezone


def convert_time_date(date_component):

    # Define a time component for 12:00 noon UTC
    time_component = time(12, 0, tzinfo=timezone.utc)

    # Combine date and time components into a single datetime object
    datetime_with_time = datetime.combine(date_component, time_component)

    return datetime_with_time


def convert_from_mountain_to_utc(datetime_obj):
    # For start date, simply add 7 hours to convert to UTC
    # Mountain time is 7 hours behind utc, so to go from mountain -> utc, we need to add
    datetime_obj += timedelta(hours=7)
    return datetime_obj

def date_strftime(date_obj, format_string):
    suffix = 'th' if 11 <= date_obj.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(date_obj.day % 10, 'th')
    return date_obj.strftime(format_string).replace('{S}', str(date_obj.day) + suffix)
