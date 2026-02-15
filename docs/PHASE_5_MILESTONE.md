# Milestone: Phase 5 - Polish & User Experience Enhancements

**Goal**
Refine the core application by adding visual clarity to AI interactions, ensuring resource efficiency with proper room lifecycle management, and implementing standard music player controls that users expect.

**Key Deliverables**
1.  **AI Visual Distinction**: A clear visual indicator in the UI (Queue) to distinguish between user-selected tracks and AI-generated "Vibe" tracks.
2.  **Robust Room Management**: Logic to handle "empty" states effectively, ensuring music stops and resources are cleaned up when the last user leaves.
3.  **Expanded Playback Controls**: Implementation of Loop/Repeat modes and Volume control to give users full command over their listening session.

## Detailed Task List

### Task 5.1: AI DJ Visual Indicator
- **Scope**: Frontend (`Queue.jsx`)
- **Description**: Update the queue item renderer to check for `added_by='system'`. Replace the generic avatar with a distinct "Robot" or "DJ" icon to visually distinguish AI contributions from user picks.
- **Acceptance Criteria**:
    - [ ] Tracks added by 'system' show unique icon.
    - [ ] Tooltips identifying "Added by AI DJ".

### Task 5.2: Empty Room Lifecycle Logic
- **Scope**: Backend (`events.py`)
- **Description**: Implement a check in the `disconnect` event. If the active user count drops to 0, the system should pause playback and potentially clean up the room resource.
- **Acceptance Criteria**:
    - [x] Playback pauses immediately when the last user disconnects.
    - [x] Room state is either archived or deleted after a set timeout (e.g., 5-10 mins).

### Task 5.3: Loop & Repeat Controls
- **Scope**: Full Stack
- **Description**: Add standard repeat functionalist.
    - **Backend**: Add `set_repeat` event handler calling Spotify `PUT /me/player/repeat`.
    - **Frontend**: Add cycle button (Off -> Context -> Track).
- **Acceptance Criteria**:
    - [ ] Clicking repeat button cycles states.
    - [ ] Spotify player state reflects the change.

### Task 5.4: Volume Control
- **Scope**: Frontend (`Player.jsx`)
- **Description**: Add a volume slider component that updates the active device's volume level via the Spotify API.
- **Acceptance Criteria**:
    - [ ] Slider controls local/remote volume.
    - [ ] Visual feedback on volume level.
