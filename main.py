import requests
import datetime
import os
import json


# saya mendeklarasikan variabel berisi API key di os demi keamanan agar API Key saya tidak dilihat publik

# api = os.getenv("MAPS_API_KEY")
# if api is None:
#     raise ValueError("API key not found")
location_data = []
destination = []
travel_time = []
fastest_place = {}

# Membuat sebuah function untuk mendapatkan koordinat dari suatu tempat berdasarkan nama tempatnya``
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
        destination.extend(place_data)
    else:
        None

    print(f"Berhasil menemukan {len(place_data)} tempat di sekitar lokasi Anda.")
    return destination


def get_travel_time(locationdata, destinationinput, api_key):
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
        "departure_time": 'now',
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


def search_bytime(travel_time):
    fastest_place = {}
    for data in travel_time:
        name = data["origin_name"]
        durations_in_seconds = data["durations_in_seconds"]
        if (
            name not in fastest_place
            or durations_in_seconds < fastest_place[name]["durations_in_seconds"]
        ):
            fastest_place[name] = data
    fastest_place_arr = list(fastest_place.values())
    
    print("\n--- Rekomendasi Tempat Tercepat ---")
    for p in fastest_place_arr:
        minutes = p['durations_in_seconds'] // 60
        print(f"Dari {p['origin_name']} ke {p['destination_name']}: {minutes} menit ({p['distance_in_meters']} meter)")


def search_byrating(destinationinput):
    max_rating = 0
    top_places = []
    for i in destinationinput:
        current_state = i.get("rating", 0)
        if current_state > max_rating:
            max_rating = current_state
            top_places = [i]
        elif current_state == max_rating:
            top_places.append(i)

    print(f"Rating Tertinggi Ditemukan: {max_rating}")
    print("Daftar Tempat dengan Rating Tersebut:\n")
    for p in top_places:
        print(f"{p.get('place_name')} : rating {p.get('rating')}")


def main():
    print("WELCOME TO PLACE RECOMMENDATION ")
    print("BY Tobias Don Bosco")
    print("-------------------------------------------------")
    api = input("Input your maps API key from https://console.cloud.google.com/ that you already create : ")

    if api is None:
        raise ValueError("API key not found")
    while True: 
        place_name = [input("Input Your Place point: ")]
        if input("Do you want to input a second point? (y/n): ") == "y":
            place_name.append(input("Input Your Second Place point:"))

        for place in place_name:
            get_place_coords(place, api)
    
        
        for detail in location_data:
            print(f"Place Name: {detail['place_name']}")
            print(f"Latitude: {detail['latitude']}")
            print(f"Longitude: {detail['longitude']}")
            print(f"Area: {detail['area']}")
        
        type_place = input("Input your type of place you want to find (e.g : hospital/restaurant/mall/university/kost/apart/etc): ")
       

        # Melakukan pencarian tempat di awal agar data tersedia untuk semua fitur
        radius = int(input("Enter the radius to search nearby places (in meters): "))
        search_nearby_place(location_data, radius, type_place, api)

        print('\nSelect the feature you want to use:')
        print('1. Search by Time (Travel Time from Origin)')
        print('2. Search by Rating')
        print('3. Exit from this program')
        choice = input('Input your choice by type the number (1/2/3): ')

        if choice == "1":
            get_travel_time(location_data, destination, api)
            search_bytime(travel_time)
        elif choice == "2":
            search_byrating(destination)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

        choice = input("Do you want to select? (y/n): ")
        
        if choice == "n":
            break

if __name__ == "__main__":
    main()