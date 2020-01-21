import datetime
import math


def valid_location(station: dict):
    if "latitude" not in station.keys():
        return False

    return (46.45629 <= station["latitude"] <= 46.51586 and
            11.29115 <= station["longitude"] <= 11.37938)


def unique_ids(data_types):
    return set([data_type[0] for data_type in data_types])


def ids_of(allowed_data_types):
    return [data_type["name"] for data_type in allowed_data_types]


def valid_data_types(data_type_ids, allowed_data_types):
    allowed_data_type_ids = ids_of(allowed_data_types)

    return list(filter(lambda it: it in allowed_data_type_ids, data_type_ids))


def mode_for(data_type_name, allowed_data_types):
    return list(filter(lambda it: it["name"] == data_type_name, allowed_data_types))[0]["mode"]


def scale(record, data_type, mode):
    minimum_period = 300
    slices_number = math.floor(record["period"] / minimum_period)

    result = []
    for index in range(slices_number):
        result.append(dict(
            data_type=data_type,
            value=record["value"] / slices_number if mode == "fraction" else record["value"],
            timestamp=record["timestamp"] - minimum_period * 1000 * index
        ))

    return result


def reverse(elements):
    return elements[::-1]


def time_frames_from(start, end, days_between_calls):
    actual = end
    while True:
        if actual <= start:
            start = actual
            break
        actual -= datetime.timedelta(days=1)

    date_range = range(0, (end - start).days + 1, days_between_calls)
    return reverse([end - datetime.timedelta(days=x) for x in date_range])


def date_from(datestring):
    return datetime.datetime.strptime(datestring, '%Y-%m-%d')


def today():
    time = datetime.datetime.now()
    return time.replace(hour=0, minute=0, second=0, microsecond=0)
