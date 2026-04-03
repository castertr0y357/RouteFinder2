# RouteFinder 🗺️

RouteFinder is an intelligent, containerized Django web application designed to help users efficiently optimize multi-stop journeys. Perfect for garage sales, real estate tours, or delivery routing, it calculates the most efficient traversal path and exports those directions seamlessly into your mobile navigation applications.

## Features ✨

- **Optimized Routing:** Pass in a starting location and a list of destination addresses, and the Route Solver intelligently computes the fastest path.
- **Google Maps Integration:** Click a single button to transform your multi-stop route into a functional Google Maps Directions URL. RouteFinder intelligently segments your journey if it pushes past Google's 10-stop URL limits.
- **User Authentication:** Robust, standard Django session management allows you to register and log in to a secure profile.
- **Persistent Profiles:** Once registered, set a persistent "Home Address" in your profile settings. The system will inherently detect you upon return and automatically pre-fill your starting location! 
- **Dockerized Environment:** Spins up reliably for development with minimum configuration needed. 

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- **Google Maps API Key**: You must provide an active Google Maps API Key securely configured via your Google Cloud Console.

## Setup Instructions 🚀

**1. Configure Secrets**
Start by setting up your environment configuration. Copy the skeleton variables to a functional `.env` file at the root of the project:
```bash
cp .env.example .env
```
Open `.env` and assign your active Google Cloud Developer API key to `GOOGLE_MAPS_API_KEY`.

**2. Spin Up the Environment**
Start the Docker container mapping your internal `web` interface securely.
```bash
docker-compose up --build
```

**3. Setup the Database**
In a separate terminal (while Docker is running), run the local Django migrations to structure your SQLite database and initialize User Authentication models.
```bash
docker-compose run web python manage.py migrate
```

## Usage 🛠️

Once running, access the web UI at [`http://localhost:8000`](http://localhost:8000).

* **Accounts:** Click `Register` in the top right to generate a user. Select `Profile` to save your permanent route starting point.
* **Calculations:** Enter your addresses—one per line—and click "Calculate Optimized Route."
* **Navigation:** Click `Open Route in Google Maps` beneath the sorted list to launch the built-in map UI seamlessly.

## Tech Stack 💻

- **Backend:** Python + Django 5.0+
- **Database:** Internal SQLite3
- **Containerization:** Gunicorn + Docker
- **APIs:** Google Maps Directions API
- **Deployment Strategy:** Local volume bound mounts for high-velocity prototyping.

## Security Overview

The `db.sqlite3` system file alongside `.env`, caching utilities, and IDE directories are natively excluded from remote pushes inside `.gitignore` ensuring that your API limits and user lists are held safely in your local build.
