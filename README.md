# Smart Multi-Stop Planner

Antigravity-ready React/Vite implementation of the Smart Multi-Stop Planner.

## Architecture

This front-end prototype uses one deterministic optimizer for priorities, opening hours, preferred arrivals, available time, and travel estimates. Its route visualization is a custom SVG illustration driven by that same optimizer output—no external map, API key, billing account, or network service is required.

## Setup & Run

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

No environment configuration is needed.

## Main file

`src/App.jsx`
