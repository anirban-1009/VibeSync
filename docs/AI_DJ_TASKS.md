# AI DJ Implementation Tasks

## Phase 1: Foundation & Data Collection

- [*] **Task 1.1: Update Spotify Permissions**
    -   **File**: `backend/app/auth.py`
    -   **Description**: Add `user-top-read` to the `SCOPE` string in the authorization URL.
    -   **Validation**: Verify that logging in presents the new permission request screen.

- [*] **Task 1.2: detailed User Profile Fetching**
    -   **File**: `backend/app/events.py` (or new `backend/app/services/spotify.py`)
    -   **Description**: Create a function to fetch a user's top tracks/artists upon `join_room`.
    -   **Note**: This should be done asynchronously to not block the socket connection.

- [*] **Task 1.3: Room State Expansion**
    -   **File**: `backend/app/state.py`
    -   **Description**: Update the room data structure to hold `vibe_profile` data (aggregated stats of users).

## Phase 2: Logic & Recommendation Engine

- [ ] **Task 2.1: Recommendation Service**
    -   **File**: `backend/app/services/recommendations.py` (New File)
    -   **Description**: Implement a function `get_recommendations(token, seeds, history, targets)` that calls the Spotify API.
    -   **Logic**:
        -   Calculate standard deviation of energy/tempo in `history` (last 5 tracks).
        -   If variance is low (monotonous), slightly shift the target parameters for the next track.
    -   **Requirements**: Handle token refresh or use a valid user token from the room.

- [ ] **Task 2.2: Aggregation Logic**
    -   **File**: `backend/app/logic/vibe.py` (New File)
    -   **Description**: Logic to calculate the "average" vibe of the room based on the users present.
    -   **Output**: A dictionary of target audio features (e.g., `energy: 0.7`).

- [ ] **Task 2.3: Mood Parser (LLM)**
    -   **File**: `backend/app/logic/mood_parser.py`
    -   **Description**: A function that takes a string input and returns Spotify Recommendation parameters.
    -   **Example**: Input "Study mode" -> `{"target_energy": 0.3, "target_instrumentalness": 0.8}`.

## Phase 3: Personality & Voice (LLM Integration)

- [ ] **Task 3.1: LLM Client Setup**
    -   **File**: `backend/app/services/llm.py` (New File)
    -   **Description**: Create a wrapper for the LLM provider. Support `OPENAI_API_KEY` or a local URL for `Ollama`.
    -   **Output**: A function `generate_dj_script(context: dict) -> str`.

- [ ] **Task 3.2: Persona Prompting**
    -   **File**: `backend/app/prompts/dj_persona.py`
    -   **Description**: Design the System Prompt. "You are DJ HAL. Be charismatic, brief, and mention users by name."
    -   **Testing**: Verify the LLM outputs short, punchy intros without hallucinating fake song data.

- [ ] **Task 3.3: TTS Service**
    -   **File**: `backend/app/services/voice.py`
    -   **Description**: Implement a function that takes the text string and returns an Audio Buffer / URL.
    -   **Note**: Use a temp directory or in-memory stream to serve this to the client.

## Phase 4: Integration & Triggers

- [ ] **Task 4.1: Auto-Queue Trigger**
    -   **File**: `backend/app/events.py`
    -   **Description**: In the `skip_song` handlers, check if `queue` is empty.
    -   **Action**: Call Recommendation Service -> Call LLM Service (for intro) -> Add to queue.

- [ ] **Task 4.2: Frontend Audio Player**
    -   **File**: `frontend/src/components/Player.jsx`
    -   **Description**: Add a secondary hidden `<audio>` element to play the DJ ID/Intro *before* the Spotify Track starts.

- [ ] **Task 4.3: Vibe Input UI**
    -   **File**: `frontend/src/components/VibeCheck.jsx`
    -   **Description**: A text input / chat bubble where users can say "I'm feeling X".
    -   **Event**: Emits `set_vibe` socket event.

## Phase 5: Polish

- [ ] **Task 5.1: Frontend Indicator**
    -   **File**: `frontend/src/components/Queue.jsx`
    -   **Description**: Visually distinguish tracks added by the AI (e.g., a robot icon instead of a user avatar).

- [ ] **Task 4.2: Empty State Handling**
    -   **File**: `backend/app/events.py`
    -   **Description**: specific logic for when the room is empty vs just 1 user.
