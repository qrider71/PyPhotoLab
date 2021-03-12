from geopy import MapQuest

geo_locator = MapQuest(api_key="utaYsA8FyZrkbM6BeQrUXEYd9REPSto5")


def get_geo_description(lat_deg, lon_deg):
    description = geo_locator.reverse("{}, {}".format(lat_deg, lon_deg))
    print (description)
