# AI DJ Feature Specification

## Overview
The **AI DJ** is an intelligent automated system designed to monitor the state of a VibeSync room and actively manage the music queue when user input is absent. Instead of simple randomization, the AI DJ analyzes the musical preferences (the "vibe") of the currently connected users to select tracks that fit the room's energy.

## Architectural Components

### 1. Data Collection ("The Ears")
To make intelligent decisions, the system must understand the users.
- **Improved Permissions**: The Spotify OAuth scope must be expanded to include `user-top-read`.
- **Room Vibe State**: A real-time aggregate of the musical preferences of all active users in the room.
- **Session History**: A robust log of the last 20 played tracks, including their audio features (Energy, Tempo).
- **Active Vibe Input**: Explicit user requests (e.g., "I want to relax", "Play something pumped up").

### 2. Decision Engine ("The Brain" - Algorithmic)
The core logic that determines *what* to play.
- **Trigger**: The AI activates when the queue is empty or nearing completion.
- **Algorithm**:
  - **Context**: The last 5 songs from `Session History`.
  - **Seeds**: Randomly selected artists/tracks from the active users in the room.
  - **Targets**:
    1.  **History Analysis**: Check if the last 3 songs had high energy (> 0.8). If so, maybe recommend a cooldown (0.6).
    2.  **Vibe Input**: Override history if a user explicitly requested a mood.
  - **Filtration**: Ensures no duplicates from the immediate history or current queue.

### 3. Personality Engine ("The Voice" - LLM)
The layer that gives the DJ a human-like presence.
- **Role**: analyzing context (who added the last song, who is active, what is the vibe) to generate natural commentary.
- **Implementation**:
  - **Hybrid Approach**: We do *not* use the LLM to pick songs (hallucination risk). We use it to *talk* about the songs.
  - **Context Window**: The LLM receives the Room State + Current Track Metadata.
  - **Output**: Short, punched-up text introductions (e.g., *"Switching gears to some high-tempo funk for Anirban!"*).

### 4. Execution ("The Hands")
- **Auto-Queueing**: The backend injects tracks into the shared queue with a special flag (`added_by: "AI_DJ"`).
- **Voice Synthesis (TTS)**: The LLM text is converted to an audio clip which plays client-side before the track starts.

## Data Structures

### Updated Room State (`state.py`)
```python
rooms[room_id] = {
    # ... existing fields ...
    "vibe_profile": {
        "users_data": {
            "user_id_1": {
                "top_genres": ["pop", "house"],
                "audio_features": {"energy": 0.8, "valence": 0.6}
            }
        },
        "room_aggregate": {
            "target_energy": 0.75,
            "target_danceability": 0.8
        }
    },
    "ai_mode_enabled": True
}
```

## API Interactions

### Spotify (Data & Audio)
1.  **`GET /me/top/tracks`**: Fetched when a user joins. Used to build their profile.
2.  **`GET /recommendations`**: Called by the AI DJ to generate the next track.

### LLM Interface (Personality & Logic)
-   **Model**: Support for local (Ollama/Llama-2/3) or Cloud (OpenAI GPT-4o-mini).
-   **Capabilities**:
    1.  **Persona**: Generating DJ patter.
    2.  **Mood Parsing**: Converting user text ("I'm sad") into Spotify Parameters (`valence: 0.2`).

### TTS (Voice)
-   **Provider**: ElevenLabs (High quality) or EdgeTTS (Free/Local).
-   **Workflow**: Text -> MP3 Buffer -> Sent to Frontend via Socket -> Played via HTML5 Audio.

## Workflow

1.  **User Joins**:
    -   Backend receives `join_room` event.
    -   Backend fetches User's Top Items (async).
    -   Backend updates `rooms[room_id]["vibe_profile"]`.

2.  **User Sets Vibe (Optional)**:
    -   User types: "Let's party!"
    -   LLM parses to: `{"min_energy": 0.8, "min_danceability": 0.7}`.
    -   State saved to `rooms[room_id]["active_vibe"]`.

3.  **Queue Check**:
    -   Triggered on `skip_song` or when a track finishes.
    -   Condition: `len(queue) == 0`.

4.  **AI Music Action**:
    -   Calculate `seed_artists` (random sample from `vibe_profile`).
    -   Apply parameters from `active_vibe` (if present) OR `vibe_profile` (average).
    -   Call Spotify Recommendations API.
    -   Add result to `queue`.

4.  **AI Voice Action** (Optional/Configurable):
    -   Context constructed: `{"next_song": "...", "vibe": "Energetic", "active_users": ["Anirban"]}`.
    -   LLM generates intro text.
    -   TTS generates audio.
    -   Audio URL attached to the Track Object in the queue.

## Future Enhancements
-   **Voice synthesis (TTS)**: Introducing tracks ("That was a banger from Anirban, here's one for the whole crew").
-   **Vibe Check UI**: Users voting 🔥 or 💧 to adjust the `target_energy` in real-time.
