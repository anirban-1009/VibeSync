# Layer & Request Flow Diagrams

## 1. High-Level Layer Architecture
This diagram shows the separation of concerns between the Presentation (Frontend), Logic (Backend Core), AI Services, and External Providers.

```mermaid
graph TD
    %% Styling
    classDef frontend fill:#282c34,stroke:#61dafb,color:white;
    classDef api fill:#4a148c,stroke:#ab47bc,color:white;
    classDef logic fill:#1b5e20,stroke:#66bb6a,color:white;
    classDef ai fill:#bf360c,stroke:#ff7043,color:white;
    classDef ext fill:#212121,stroke:#757575,color:white;

    subgraph Presentation_Layer ["Presentation Layer"]
        UI[React UI]:::frontend
        SocketClient[Socket.IO Client]:::frontend
        AudioEngine[HTML5 Audio + Spotify SDK]:::frontend
    end

    subgraph API_Layer ["API & Event Layer"]
        SocketServer[Socket.IO Server]:::api
        AuthRouter[OAuth Router]:::api
    end

    subgraph Logic_Layer ["Business Logic Layer"]
        RoomManager[Room State Manager]:::logic
        QueueManager[Queue Controller]:::logic
        VibeAggregator[Vibe Calculator]:::logic
    end

    subgraph AI_Service_Layer ["AI & Intelligence Layer"]
        LLM_Service[LLM Wrapper - Mood Persona]:::ai
        TTS_Service[Voice Generator]:::ai
        Rec_Service[Spotify Recommendation Engine]:::ai
    end

    subgraph Data_Layer ["Data & External"]
        SpotifyAPI[Spotify API]:::ext
        LLM_Model[Ollama / OpenAI]:::ext
        TTS_Provider[ElevenLabs]:::ext
    end

    %% Connections
    UI -- User Input --> SocketClient
    SocketClient -- Socket Events --> SocketServer

    SocketServer --> RoomManager

    RoomManager -- Queue Empty? --> QueueManager
    RoomManager -- New Vibe? --> VibeAggregator

    VibeAggregator -- Current User Stats --> Rec_Service
    VibeAggregator -- User Text Input --> LLM_Service

    Rec_Service -- Get Tracks --> SpotifyAPI
    LLM_Service -- Parse Mood --> LLM_Model

    QueueManager -- Get Next Song --> Rec_Service
    QueueManager -- Generate Intro --> LLM_Service
    LLM_Service -- Intro Text --> TTS_Service
    TTS_Service -- Synthesize --> TTS_Provider

    QueueManager -- Update Room --> SocketServer
    SocketServer -- New Track + Audio URL --> SocketClient
```

---

## 2. Request Flow: "User Sets Vibe & AI Responds"
This sequence diagram illustrates the specific flow when a user says "I want to relax," triggering the entire chain.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend (Events)
    participant LLM_Service
    participant Spotify_Recs
    participant TTS_Service

    Note over User, Frontend: User types: "I want to chill"

    User->>Frontend: Clicks "Send Vibe"
    Frontend->>Backend (Events): emit('set_vibe', { text: "I want to chill" })

    activate Backend (Events)
    Backend (Events)->>LLM_Service: parse_mood("I want to chill")
    activate LLM_Service
    LLM_Service-->>Backend (Events): return { target_energy: 0.3, target_valence: 0.5 }
    deactivate LLM_Service

    Backend (Events)->>Backend (Events): Update Room State (active_vibe)
    Backend (Events)-->>Frontend: emit('vibe_updated')

    Note over Backend (Events): ...Music Queue Runs Out...

    Backend (Events)->>Spotify_Recs: get_recommendations(seeds, active_vibe)
    activate Spotify_Recs
    Spotify_Recs-->>Backend (Events): Track: "Weightless" (Marconi Union)
    deactivate Spotify_Recs

    Backend (Events)->>LLM_Service: generate_intro(Track="Weightless", Context="Chill Mode")
    activate LLM_Service
    LLM_Service-->>Backend (Events): "Taking it down a notch for everyone."
    deactivate LLM_Service

    Backend (Events)->>TTS_Service: speak("Taking it down a notch...")
    activate TTS_Service
    TTS_Service-->>Backend (Events): AudioURL (blob/stream)
    deactivate TTS_Service

    Backend (Events)->>Backend (Events): Add Track + AudioURL to Queue
    Backend (Events)-->>Frontend: emit('queue_updated')

    deactivate Backend (Events)

    Note over Frontend: Player plays AudioURL (Voice) -> Then Spotify Track
```
