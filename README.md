# RouteFinder 2.0: The Nocturnal Navigator 🗺️🧠

RouteFinder 2.0 is a professional-grade, AI-powered tactical scouting suite for the modern explorer. No longer just a mapping tool, the **Nocturnal Navigator** uses local Large Language Models (LLMs) and predictive analytics to identify high-value resale opportunities before you even leave your driveway.

![Mission Control UI](file:///C:/Users/caste/.gemini/antigravity/brain/06949b7a-1c13-4e52-a150-38485bd07d4e/media__1777069589337.png)

---

## 🧠 The AI Scouting Engine (Powered by Gemma)
At the heart of RouteFinder 2.0 is a local **Ollama** integration running **Gemma:4b**. Every listing you discover is subjected to a deep tactical scan:

- **💎 Hidden Goldmine Detection**: AI identifies short, vague descriptions in high-affluence zip codes—the hallmark of "unpicked" estate gems.
- **💸 Arbitrage & Profit Scouting**: Automatically flags mentions of high-resale brands (Nikon, Le Creuset, Power Tools) with **PROFIT POTENTIAL** badges.
- **🎯 Wishlist Matchmaking**: Scans every listing against your personal "Looking For" list and highlights matches with surgical precision.
- **📂 Intelligent Neighborhood Clustering**: Semantically groups community-wide sales to prevent redundant stops and maximize your time-on-ground.

## 🚀 Donation Surge Predictive Engine
RouteFinder 2.0 introduces the **Donation Surge Proxy**, a first-of-its-kind predictive tool for thrift shoppers:
- **The Logic**: The system cross-references local garage sale activity with nearby thrift stores.
- **The Trigger**: If a cluster of **"Moving" or "Downsizing"** sales is detected in a zip code, local thrift stores are flagged with a **🚀 RECENT DONATION SURGE** badge.
- **The Advantage**: You'll know exactly which stores just received a high-volume influx of fresh, quality donations.

## 💎 Tactical Badge System (HUD)
Your discovery grid is enriched with high-intensity visual badges:
- **🚀 RECENT DONATION SURGE**: High probability of fresh thrift inventory.
- **💸 PROFIT POTENTIAL**: High-resale items detected by AI.
- **💎 POTENTIAL GOLDMINE**: High-end area with unvetted descriptions.
- **🔒 COMMUNITY LOCK**: Prevents double-booking stops at the same neighborhood event.
- **⚠️ BUST HISTORY**: Alerts you if an address was a "bust" in the past.

---

## ✨ Premium Core Features
- **Multi-Mode Discovery**: Pivot instantly between **Garage Sale** listings and **Thrift Store** storefronts.
- **Intelligent TSP Routing**: Automated route calculation with support for **Manual Priorities**. Fix certain stops while the engine optimizes the rest.
- **"Mission Control" UI**: A premium, high-contrast dark-mode interface with glassmorphism effects and mechanical dual-gear loading animations.
- **Progressive Web App (PWA)**: Install directly to your iOS or Android home screen for a full-screen, native-app experience.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Ollama](https://ollama.ai/) installed and running locally with `gemma:4b` pulled.
- [Google Maps API Key](https://console.cloud.google.com/google/maps-apis/credentials) with **Directions**, **Distance Matrix**, and **Places** APIs enabled.

### 2. Launch the Tactical Stack
RouteFinder is fully orchestrated. A single command handles the database, migrations, and superuser injection:
```bash
docker-compose up --build
```
Access the dashboard at `http://localhost:8000`.

---

## 💻 Technical Hardening
RouteFinder 2.0 is built for stability and speed:
- **Hardened Scraper Session**: Parallel, connection-pooled scrapers with automatic retries and browser-spoofing headers.
- **Gunicorn 120s Timeout**: Optimized for heavy AI scouting missions.
- **Chunked AI Processing**: Massive result sets are analyzed in focused batches to maintain LLM accuracy and prevent context exhaustion.
- **Postgres Backbone**: Professional-grade data persistence for your ratings and history.

---

## 🔒 Administrative Lockdown
- **Administrative Gate**: Protect your Google Maps quota with a mandatory login.
- **Manual Approvals**: New user registrations must be approved by the `/admin` to prevent unauthorized access.

---
*Developed for explorers who demand superior intel.* 🛰️🗺️
