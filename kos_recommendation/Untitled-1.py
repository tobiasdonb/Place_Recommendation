# %%
import requests
import datetime
import os
import json

# %%
# sebelumnya saya sudah mendeklarasikan variabel berisi API key di os demi keamanan code
api = os.getenv("MAPS_API_KEY")
if api is None:
    raise ValueError("API key not found")

# %%
location_data = []

# %%


def get_place_coords(place_name, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place_name, "key": api_key}
    res = requests.get(url, params=params)
    data = res.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        area = data["results"][0]["formatted_address"]
        place_data = {
            "place_name": place_name,
            "latitude": location["lat"],
            "longitude": location["lng"],
            "area": area,
        }
        if place_data not in location_data:
            location_data.append(place_data)
        else:
            None

        return place_data
    else:
        return None


# %%
get_place_coords("MCD SANUR", api)

# %%
get_place_coords("PLAZA RENON", api)

# %%
location_data

# %%
destination = []

# %%
# saya ingin download dan merapikan data json yang di crate API agar mudah saya baca
download_json = []


# %%
def search_nearby_place(locationdata, radius_meters, type_place, api_key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # latitude dan longitude centroid berdasarkan rata2 latitude dan longitude
    # untuk mencari titik tengah dari lokasi-lokasi yang kita masukkan,terinsiprasi dari k means clustering
    all_latitude = [place["latitude"] for place in locationdata]
    all_longitude = [place["longitude"] for place in locationdata]

    lat_centroid = sum(all_latitude) / len(all_latitude)
    lng_centroid = sum(all_longitude) / len(all_longitude)

    params = {
        "location": f"{lat_centroid},{lng_centroid}",
        "radius": radius_meters,
        "type": type_place,
        "key": api_key,
    }

    res = requests.get(url, params=params)
    data = res.json()

    # ARSIP
    # return data

    # sebelum lanjut membuat code untuk menambahkan data ke variabel destination,saya akan coba download file json/var datanya
    # bertujuan agar saya dapat melihat struktur data agar mudah dirapikan dan dimasukan ke variable destination
    # download_json.append(data)

    # setelah download data dan melihat struktur data json,saya lanjut mengambil 3 parameter utama berdasar struktur json yang sudah saya baca
    place_data = [
        {
            "place_name": place["name"],
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "rating": place.get("rating", 0),
        }
        for place in data["results"]
    ]

    if place_data not in destination:
        destination.append(place_data)
    else:
        None

    return place_data


# %%
search_nearby_place(location_data, 4000, "hospital", api)

# %%
destination

# %%
# tadi kan destination variable itu list dalam list krna saya loop pakai list comprehension,jadi saya flatten
destination_flatten = destination[0]

# %%
# ARSIP

# with open("nearby_search.json","w") as f:
#         json.dump(download_json,f)
# download_json.clear()

# %%
destination_flatten

# %%
travel_time = []

# %%


def get_travel_time(locationdata, destinationinput, departure_time, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    # for sublist in destination:
    #     destination_flattten.extend(sublist)
    # format untuk latitude longitude ke google api menggunakan |
    origin = "|".join([f"{o['latitude']},{o['longitude']}" for o in locationdata])
    destination_coor = "|".join(
        [f"{d['latitude']},{d['longitude']}" for d in destinationinput]
    )
    params = {
        "origins": origin,
        "destinations": destination_coor,
        "mode": "driving",
        "departure_time": departure_time,
        "key": api_key,
    }
    res = requests.get(url, params=params)
    data = res.json()

    # ARSIP

    # sebelum lanjut membuat code untuk menambahkan data ke variabel travel_time,saya akan coba download file json/var datanya
    # bertujuan agar saya dapat melihat struktur data agar mudah dirapikan dan dimasukan ke variable travel_time
    # download_json.append(data)

    # merapikan variabel data,menam
    for i, row in enumerate(data["rows"]):
        origin_name = locationdata[i]["place_name"]
        for j, element in enumerate(row["elements"]):
            destination_name = destinationinput[j]["place_name"]
            alamat = data["destination_addresses"][j]
            durations = element["duration_in_traffic"]["value"]
            distance_in_meters = element["distance"]["value"]
            travel_time.append(
                {
                    "origin_name": origin_name,
                    "destination_name": destination_name,
                    "durations_in_seconds": durations,
                    "distance_in_meters": distance_in_meters,
                    "alamat": alamat,
                }
            )


# %%
get_travel_time(location_data, destination_flatten, "now", api)

# %%
# Arsip
# with open("distance_matrix.json","w") as f:
#         json.dump(download_json,f)
# download_json.clear()

# %%
travel_time

# %%

fastest_place = {}

for data in travel_time:
    name = data["origin_name"]
    distance_in_meters = data["distance_in_meters"]
    if (
        name not in fastest_place
        or distance_in_meters < fastest_place[name]["distance_in_meters"]
    ):
        fastest_place[name] = data
fastest_place_arr = list(fastest_place.values())


# %%
fastest_place_arr


# %%
def search_byrating(destinationinput):
    max_rating = 0
    for i in destination_flatten:
        current_state = i.get("rating", 0)
        if current_state > max_rating:
            max_rating = current_state

    top_places = []
    for x in destination_flatten:
        if x.get("rating", 0) == max_rating:
            top_places.append(x)

    print(f"Rating Tertinggi Ditemukan: {max_rating}")
    print("Daftar Tempat dengan Rating Tersebut:\n")
    for p in top_places:
        print(f"{p.get('place_name')} : rating {p.get('rating')}")


# %%
search_byrating(destination_flatten)

# %% [markdown]
#

# %%
