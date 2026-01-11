# VibeSync

<div align="center">
  <img src="frontend/public/favicon.png" alt="VibeSync Logo" width="120" />
  <p>
    <strong>Real-time Collaborative Music Listening Platform</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="Socket.io" />
    <img src="https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify" />
  </p>
</div>

---

## Overview

VibeSync is a modern web application that allows users to create rooms and listen to music together in real-time. Built with a React frontend and a FastAPI backend, it utilizes WebSockets to synchronize playback state across all connected clients, ensuring everyone hears the same beat at the same time.

## Key Features

- **Real-time Synchronization**
  Playback status, current track, and timestamp are synchronized instantly across all users in a room. If one person pauses or skips, it updates for everyone.

- **Collaborative Queue**
  Users can search for songs via the Spotify API and add them to a shared room queue.

- **History & Re-queue**
  Keep track of what has been played. History items show who added the song and allow for one-click re-queuing of favorite tracks.

- **User Presence**
  See who is currently online in the room. Each action (adding a song) is tagged with the user's avatar, adding a social layer to the listening experience.

- **Spotify Integration**
  Seamlessly integrates with Spotify Premium accounts for high-quality audio streaming directly in the browser.

## Architecture

The project is structured as a modular monolith with a clear separation of concerns:

- **Frontend**: React, Vite, Socket.IO Client
- **Backend**: Python, FastAPI, Python-SocketIO, Spotipy

For a detailed technical breakdown, please refer to the [Architecture Documentation](docs/architecture.md).

## Getting Started

### Prerequisites

- Node.js & npm
- Python 3.8+
- Spotify Premium Account
- Spotify Developer Application (Client ID & Secret)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd dj-jam-room
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    uv sync
    
    # Create .env file
    # Ensure CLIENT_ID, CLIENT_SECRET, and FRONTEND_URL are set
    uv run uvicorn app.server:socket_app --reload
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

4.  **Access the App**
    Open your browser to `http://localhost:5173` (or your configured frontend URL).

## Usage

1.  **Login**: Authenticate with your Spotify account.
2.  **Join/Create**: Enter a Room ID to start a new session or join an existing one.
3.  **Invite**: Click "Share" to copy the room link and send it to friends.
4.  **Jam**: Search for songs, add them to the queue, and enjoy the synchronized music experience.
