# 🛰️ RouteFinder 2.0: The Nocturnal Navigator
### Tactical AI-Powered Garage Sale Scouting & Routing Suite

RouteFinder 2.0 is a production-hardened, high-intensity scouting suite designed for serious treasure hunters. It combines real-time data scraping, Gemma-powered AI analysis, and tactical route optimization into a single, mobile-ready interface.

---

## 🛠️ Tactical Features

### 📡 1. Strategic Discovery
*   **Real-Time Scouring**: Deep-scrapes multiple data sources for garage sales and estate auctions.
*   **Thrift Recon**: Integrated Google Places intelligence to locate and analyze thrift stores, including real-time "Donation Surge" probability detection.
*   **The Vault (Saved Intel)**: Persistence layer that allows you to scout on Friday night and instantly load your mission on Saturday morning across any device.

### 🧠 2. AI Intelligence Engine
*   **Tactical Badging**: Gemma AI analyzes listing descriptions to identify high-value targets.
    *   ⚠️ **BUST CANDIDATE**: AI identifies probable waste-of-time listings based on keywords and history.
    *   ✨ **TREASURE DETECTED**: Highlights rare items, antiques, or high-value electronics.
    *   🎯 **MATCH FOUND**: Cross-references listings against your personal **Wishlist**.
*   **Community Clustering**: Automatically identifies neighborhood-wide events and multi-family sales.

### 🏁 3. Precision Execution
*   **Tactical Route Solver**: Optimizes your route for maximum efficiency, minimizing drive time and maximizing "Booty Per Hour" (BPH).
*   **Mobile "Tactical Stack"**: Responsive UI designed for one-handed operation in the field, with high-contrast night mode support.

### 📱 4. Progressive Web App (PWA)
*   **Native Experience**: Installable on iOS and Android for a full-screen, standalone experience.
*   **Network-First Resilience**: Optimized caching ensures the app remains responsive even in low-signal cellular dead zones.

---

## 🚀 Quick Deployment (Docker)

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/castertr0y357/RouteFinder2.git
    cd RouteFinder2
    ```

2.  **Configure Environment**:
    Create a `.env` file based on the provided examples:
    ```env
    GOOGLE_MAPS_API_KEY=your_api_key_here
    DEFAULT_ADMIN_USER=admin
    DEFAULT_ADMIN_PASSWORD=your_secure_password
    # Required for HTTPS production domains:
    CSRF_TRUSTED_ORIGINS=https://your-domain.com
    ```

3.  **Launch the Fleet**:
    ```bash
    docker compose up -d --build
    ```

4.  **Access the Bridge**:
    Navigate to `http://localhost:8000` (or your server's IP).

---

## 💾 Database Backups & Recovery

The suite includes an automated utility to back up and restore the database (supporting both SQLite and PostgreSQL):

*   **Perform Backup**:
    ```bash
    python backup_db.py
    ```
    This dumps the database to a compressed, timestamped file in the `backups/` directory (e.g., `backups/backup_20260613_120000.sqlite3.gz`).

*   **Restore Backup**:
    ```bash
    python backup_db.py --restore backups/backup_20260613_120000.sqlite3.gz
    ```

---

## 📱 Mobile Installation

*   **Android (Chrome)**: Tap the **📲 INSTALL APP** button in the header or select "Add to Home Screen" from the Chrome menu.
*   **iOS (Safari)**: Tap the **Share** icon (square with up arrow) and select **"Add to Home Screen"**.

---

## ℹ️ Tactical Briefing
New to the suite? Click the **ℹ️ BRIEFING** button in the header for a guided tour of the Discovery, Intelligence, and Execution phases.

---

*Developed with ❤️ for the elite scouting community.*
