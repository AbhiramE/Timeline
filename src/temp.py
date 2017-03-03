import requests
from datetime import date


def get_geo_address(top_10):
    top_10_addresses = []
    for latlong in top_10:
        payload = {'latlng': str(latlong[0]) + ',' + str(latlong[1])}
        r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload)
        print(r.url)
        result = r.json()
        print(result['results'][0]['formatted_address'])
        top_10_addresses.append(result['results'][0]['formatted_address'])

    return top_10_addresses


def first_day_of_last_month(d):
    if d.month == 1:
        return date(d.year - 1, 12, 1)
    else:
        return date(d.year, d.month - 1, 1)

print(first_day_of_last_month(date.today()))
