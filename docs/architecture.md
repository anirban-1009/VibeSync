
# VibeSync Architecture

VibeSync is a real-time collaborative music listening application. It uses a clean, modular architecture separating the React frontend from the Python FastAPI backend, communicating primarily over WebSockets for real-time state synchronization.

## System Overview

The application follows a client-server model where:
- **Frontend**: Handles user interaction, music playback via Spotify SDK, and state visualization.
- **Backend**: Manages room states, user presence, queues, and history using in-memory storage.
- **Socket.IO**: Facilitates bidirectional, real-time communication for events like "play", "pause", "skip", and "queue update".

## Architecture Diagram

```mermaid
graph TD
    %% Styling
    classDef frontend fill:#282c34,stroke:#61dafb,stroke-width:2px,color:white;
    classDef backend fill:#1f4037,stroke:#3fb950,stroke-width:2px,color:white;
    classDef external fill:#121212,stroke:#1db954,stroke-width:2px,color:white;

    subgraph Client_Side ["Frontend (React + Vite)"]
        direction TB
        App[App.jsx <br/>Central State Manager]:::frontend

        subgraph UI_Components ["UI Components"]
            Login:::frontend
            JoinRoom:::frontend
            RoomHeader:::frontend
            Player:::frontend
            Search:::frontend
            Queue:::frontend
        end

        SpotifySDK[Spotify Web Playback SDK]:::external

        App --> Login
        App --> JoinRoom
        App --> RoomHeader
        App --> Player
        App --> Search
        App --> Queue
        App -.->|Init & Control| SpotifySDK
    end

    subgraph Server_Side ["Backend (FastAPI + Python-SocketIO)"]
        direction TB
        Main[main.py <br/>Entry Point]:::backend
        ServerConf[server.py <br/>App Init]:::backend
        Auth[auth.py <br/>OAuth Routes]:::backend
        Events[events.py <br/>Socket Event Handlers]:::backend
        State[state.py <br/>Global State Store]:::backend

        subgraph AI_Layer ["AI Services"]
            Logic[logic/vibe.py <br/>Math & Aggregation]:::backend
            LLM[services/llm.py <br/>LangChain/Ollama]:::backend
            TTS[services/voice.py <br/>Text-to-Speech]:::backend
        end

        Main --> ServerConf
        Main --> Auth
        Main --> Events
        Events -->|Read/Write| State
        Events -->|Trigger| Logic
        Logic -->|Request Intro| LLM
        LLM -->|Generate Audio| TTS
        Auth -->|Server Config| ServerConf
    end

    subgraph External_Services ["External Services"]
        SpotifyAPI[Spotify Web API]:::external
        SpotifyAccounts[Spotify Accounts Service]:::external
        LLM_Provider[Ollama / OpenAI]:::external
        TTS_Provider[ElevenLabs / EdgeTTS]:::external
    end

    %% Data Flow Connections
    App <==>|Real-time Events via Socket.IO| Events
    App -->|Auth Request| Auth

    Auth -.->|Redirect| SpotifyAccounts
    SpotifyAccounts -.->|Callback Code| Auth

    App -->|Search & Metadata via REST| SpotifyAPI
    SpotifySDK <==>|Audio Stream| SpotifyAPI
    Events -.->|Get Recs| SpotifyAPI

    LLM -.->|Inference| LLM_Provider
    TTS -.->|Synthesis| TTS_Provider
```

## Module Descriptions

### Frontend (`frontend/src/`)
*   **`App.jsx`**: The root container. It initializes the Socket connection, manages the Spotify Player instance, and holds the global application state (current track, queue, users).
*   **`components/Player.jsx`**: Visualizes the current song, progress bar, and playback controls.
*   **`components/Queue.jsx`**: Displays the "Up Next" queue and "History" tabs. Handles removal and re-queuing of tracks.
*   **`components/Search.jsx`**: Provides a search bar tapping into the Spotify API to add songs to the room.
*   **`components/RoomHeader.jsx`**: Shows room info and a list of active users (avatars).

### Backend (`backend/app/`)
*   **`main.py`**: The application entry point. It imports the routers and runs the Uvicorn server.
*   **`server.py`**: Initializes the `FastAPI` app and the `Socket.IO` server instance.
*   **`events.py`**: Business logic hub (Socket Events). Now acts as the "Controller" for the AI DJ.
*   **`state.py`**: Holds `vibe_profile` and `active_vibe` alongside the standard room state.
*   **`services/`**:
    *   **`llm.py`**: Wraps the LLM provider (Ollama/OpenAI) for handling Persona generation and Mood Parsing.
    *   **`voice.py`**: Wraps the TTS provider to generate MP3s.
*   **`logic/`**:
    *   **`vibe.py`**: Pure functions to calculate average energy/valence from a list of user profiles.

## AI DJ Data Flow
1.  **Input**: User types "I'm sad" -> Frontend emits `set_vibe`.
2.  **Parsing**: `events.py` calls `llm.parse_mood("I'm sad")` -> Returns `{"seed_genres": ["sad", "rainy-day"]}`.
3.  **State Update**: Stored in `rooms[room_id]["active_vibe"]`.
4.  **Auto-Queue**:
    *   Queue runs empty.
    *   `logic.get_recommendations()` called with `active_vibe`.
    *   Spotify API returns "Sad Songs".
    *   `llm.generate_intro(song, "sad")` called.
    *   `tts.speak(intro)` called.
    *   New Track Object (with Audio URL) pushed to Queue.


## Data Flow
1.  **Authentication**: User clicks login -> Redirects to Spotify -> Callback to Backend -> Token returned to Frontend.
2.  **Room Join**: Client connects sets up Socket -> Emits `join_room` -> Backend adds user to `state`.
3.  **Playback**: User adds song -> Backend updates `queue` -> Broadcasts `room_state` -> All Clients receive update -> If playing, Client SDKs start audio.
