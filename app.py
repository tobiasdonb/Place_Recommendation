from flask import Flask, request, jsonify, render_template
from main import (
    get_place_coords,
    search_nearby_place,
    get_travel_time,
    search_bytime,
    search_byrating,
)

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/coords", methods=["POST"])
def coords():
    """Get coordinates for one or two place names."""
    body = request.get_json()
    api_key = body.get("api_key")
    places = body.get("places", [])  # list of place name strings

    if not api_key or not places:
        return jsonify({"error": "api_key and places are required"}), 400

    location_data = []
    for name in places:
        result = get_place_coords(name, api_key)
        if result:
            location_data.append(result)
        else:
            return jsonify({"error": f"Could not find coordinates for '{name}'"}), 404

    return jsonify({"location_data": location_data})


@app.route("/api/nearby", methods=["POST"])
def nearby():
    """Search nearby places around the centroid of given locations."""
    body = request.get_json()
    api_key = body.get("api_key")
    location_data = body.get("location_data", [])
    radius = body.get("radius", 1000)
    type_place = body.get("type_place", "restaurant")

    if not api_key or not location_data:
        return jsonify({"error": "api_key and location_data are required"}), 400

    # search_nearby_place extends the list you pass in and returns it
    destination = []
    result = search_nearby_place(location_data, radius, type_place, api_key)
    return jsonify({
        "destination": result["places"],
        "centroid": result["centroid"]
    })


@app.route("/api/travel-time", methods=["POST"])
def travel_time_route():
    """Get travel times from origins to destinations, then return fastest per origin."""
    body = request.get_json()
    api_key = body.get("api_key")
    location_data = body.get("location_data", [])
    destination = body.get("destination", [])
    centroid = body.get("centroid")

    if not api_key or not location_data or not destination or not centroid:
        return jsonify({"error": "api_key, location_data, destination, and centroid are required"}), 400

    travel_time = get_travel_time(location_data, destination, api_key, centroid)

    fastest = {}
    for data in travel_time:
        name = data["origin_name"]
        if name not in fastest or data["durations_in_seconds"] < fastest[name]["durations_in_seconds"]:
            fastest[name] = data

    return jsonify({"travel_time": travel_time, "fastest": list(fastest.values())})


@app.route("/api/rating", methods=["POST"])
def rating_route():
    """Return the highest-rated places from a destination list."""
    body = request.get_json()
    destination = body.get("destination", [])

    if not destination:
        return jsonify({"error": "destination is required"}), 400

    max_rating = 0
    top_places = []
    for place in destination:
        current = place.get("rating", 0)
        if current > max_rating:
            max_rating = current
            top_places = [place]
        elif current == max_rating:
            top_places.append(place)

    return jsonify({"max_rating": max_rating, "top_places": top_places})


if __name__ == "__main__":
    app.run(debug=True)
