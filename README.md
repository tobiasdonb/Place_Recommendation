📍 Location-Based Place Scraper (Google Places API)

This project scrapes nearby places using the Google Places API by defining a search area between two or more geographic points.

🔧 How It Works

The user provides two or more reference locations (latitude & longitude).

A centroid is computed by taking the mean of all coordinate points
(inspired by the K-means clustering algorithm).

A configurable radius is applied around the centroid to define the search area.

The Google Places API is queried to retrieve target locations (e.g., restaurants, hospitals).

Results can be sorted by:

Distance to a specific reference point

Google rating



🧠 Concepts Used

Geospatial calculations

API integration

Clustering-inspired centroid computation
