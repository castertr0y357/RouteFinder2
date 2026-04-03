# RouteFinder 🗺️

RouteFinder is a premium, high-performance web optimization suite designed for weekend explorers. Whether you're hunting for the best garage sales, scouting thrift store inventory, or planning a multi-stop estate tour, RouteFinder uses intelligent TSP (Traveling Salesperson) algorithms to calculate the most efficient path for your journey.

![RouteFinder UI](file:///C:/Users/caste/.gemini/antigravity/brain/bf2a7874-f468-4e6a-9b30-0f5d55fac3aa/routefinder_logo_1775224752939.png)

## ✨ Premium Features

- **Multi-Mode Discovery**: Pivot instantly between temporary **Garage Sale** listings and permanent **Thrift Store** storefronts using Google Places intelligence.
- **Intelligent Routing**: Automated route calculation with support for **Manual Priorities**. Fix certain stops in a specific sequence while the engine optimizes the rest.
- **Visual Intelligence**: Custom Google Maps integration with color-coded markers:
  - 🟢 **Emerald**: Garage Sales.
  - 🟣 **Purple**: Thrift Stores.
  - 🟡 **Gold**: Historical "Great Find" locations.
  - 🔴 **Crimson**: Historical "Bust" locations (to avoid repeat mistakes).
- **Proactive Security**: Entire application locked behind an administrative gate to protect your Google Maps API quota. 
- **Modern "Carbon" Aesthetic**: Fully responsive, high-contrast dark-mode interface with glassmorphism effects for a premium mobile experience.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Google Maps API Key](https://console.cloud.google.com/google/maps-apis/credentials) with **Directions**, **Distance Matrix**, and **Places** APIs enabled.

### 2. Configure Environment
Create a `.env` file in the root directory:
```bash
# API Keys
GOOGLE_MAPS_API_KEY=your_key_here

# App Ports
APP_PORT=8000

# Automated Admin Provisioning
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=adminpass123

# Database (Postgres)
POSTGRES_DB=routefinder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Launch the Stack
RouteFinder is fully orchestrated. A single command handles database setup, migrations, and superuser injection:
```bash
docker-compose up --build
```
Access the dashboard at `http://localhost:8000`.

---

## 📱 Mobile Setup (Pro-Tip)

RouteFinder is designed as a **Progressive Web App (PWA)**, making it look and feel like a native application on your phone without needing an App Store.

### 🍏 iOS (Safari)
1. Open `http://your-server-ip:8000` in Safari on your iPhone.
2. Tap the **Share** icon (square with an up arrow) at the bottom.
3. Scroll down and tap **"Add to Home Screen."**
4. The RouteFinder logo will now appear on your home screen for instant, full-screen access!

### 🤖 Android (Chrome)
1. Open the URL in Chrome.
2. Tap the **Three Dots (⋮)** in the top right.
3. Tap **"Install app"** or **"Add to Home screen."**
4. Follow the prompts to add it to your launcher.

---

## 💻 Tech Stack
- **Engine**: Django 5.0+ (Python 3.11)
- **Database**: PostgreSQL 15 (Docker Sidecar)
- **Visuals**: Vanilla CSS (Glassmorphism) + Google Maps JavaScript API
- **Serving**: Gunicorn + Whitenoise
- **DevOps**: Docker Compose Orchestration

## 🔒 Administrative Lockdown
- **Pending Approvals**: New user registrations are automatically set to `Disabled`. The administrator must log into the `/admin` dashboard to manually approve new users.
- **Auto-Superuser**: If the database is fresh, the system will auto-inject the admin credentials provided in your `.env` on every startup.
