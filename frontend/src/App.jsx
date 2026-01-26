
import { useEffect, useRef, useState } from 'react'
import io from 'socket.io-client'
import './styles/App.css'

// Components
import JoinRoom from './components/JoinRoom'
import Login from './components/Login'
import Player from './components/Player'
import Queue from './components/Queue'
import RoomHeader from './components/RoomHeader'
import Search from './components/Search'
import VibeCheck from './components/VibeCheck'


import { logger } from './utils/logger'
import { VERSION } from './version'

// Connect to the backend
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const socket = io(BACKEND_URL)

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected)
  const [roomId, setRoomId] = useState('')
  const [joinedRoom, setJoinedRoom] = useState(null)
  const [activeVibe, setActiveVibe] = useState(null)

  const [token, setToken] = useState(null)
  const [player, setPlayer] = useState(null)
  const [deviceId, setDeviceId] = useState(null)

  const [userProfile, setUserProfile] = useState(null)
  const [usersInRoom, setUsersInRoom] = useState([])

  const [currentTrack, setCurrentTrack] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [queue, setQueue] = useState([])
  const [history, setHistory] = useState([])
  const [activeTab, setActiveTab] = useState('queue')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  const [logs, setLogs] = useState([])

  useEffect(() => {
    logger.debug('Current Room Users State:', usersInRoom)
  }, [usersInRoom])


  const searchTimeout = useRef(null)

  useEffect(() => {
    // Check for token in URL or LocalStorage
    const params = new URLSearchParams(window.location.search)
    const urlToken = params.get('token')

    if (urlToken) {
      setToken(urlToken)
      localStorage.setItem('spotify_access_token', urlToken)
      window.history.replaceState({}, document.title, "/")
    } else {
      const storedToken = localStorage.getItem('spotify_access_token')
      if (storedToken) {
        setToken(storedToken)
      }
    }
  }, [])

  // Fetch User Profile
  useEffect(() => {
    if (!token) return;

    fetch('https://api.spotify.com/v1/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setUserProfile(data)
      })
      .catch(err => { })
  }, [token])

  useEffect(() => {
    if (!token) return

    // Load Spotify Web Playback SDK
    const script = document.createElement("script");
    script.src = "https://sdk.scdn.co/spotify-player.js";
    script.async = true;

    document.body.appendChild(script);

    window.onSpotifyWebPlaybackSDKReady = () => {
      const player = new window.Spotify.Player({
        name: 'VibeSync Web Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
      });

      player.addListener('ready', ({ device_id }) => {
        setDeviceId(device_id);
        addLog(`Spotify Player Ready: ${device_id}`)
      });

      player.addListener('not_ready', ({ device_id }) => {
        logger.warn('Device ID has gone offline', device_id);
      });

      player.addListener('authentication_error', ({ message }) => {
        logger.error('Authentication Error:', message);
        setToken(null)
        localStorage.removeItem('spotify_access_token')
      });

      player.addListener('player_state_changed', state => {
        if (!state) return;
        setProgress(state.position)
        setDuration(state.duration)
      });

      player.connect();
      setPlayer(player);
    };

    return () => {
      if (player) player.disconnect()
    }
  }, [token])


  useEffect(() => {
    function onConnect() {
      setIsConnected(true)
      addLog('Connected to server')

      const params = new URLSearchParams(window.location.search)
      const urlRoom = params.get('room')
      const targetRoom = urlRoom || joinedRoom

      if (targetRoom) {
        const currentToken = token || localStorage.getItem('spotify_access_token');
        addLog(`Re-joining room: ${targetRoom}`)
        socket.emit('join_room', { room_id: targetRoom, user_profile: userProfile, token: currentToken })
        if (!joinedRoom) setJoinedRoom(targetRoom)
      }
    }

    function onDisconnect() {
      setIsConnected(false)
      addLog('Disconnected')
    }

    function onRoomState(state) {
      setCurrentTrack(state.current_track)
      setIsPlaying(state.is_playing)
      setQueue(state.queue)
      if (state.history) setHistory(state.history)
      if (state.users) setUsersInRoom(state.users)

      // Sync player local state if needed
      if (state.current_track && player) {
        if (state.is_playing) player.resume()
        else player.pause()
      }
    }

    function onUserListUpdated(users) {
      setUsersInRoom(users)
    }

    function onQueueUpdated(newQueue) {
      setQueue(newQueue)
    }

    function onVibeUpdated(data) {
      setActiveVibe(data.vibe)
      addLog(`Vibe Shift: ${data.vibe}`)
    }

    async function onPlayTrack(track) {
      setCurrentTrack(track)
      setIsPlaying(true)
      addLog(`Now Playing: ${track.name}`)

      if (!deviceId || !token) return

      try {
        const response = await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
          method: 'PUT',
          body: JSON.stringify({ uris: [track.uri] }),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          logger.error('Spotify API Error:', errorData);
        }
      } catch (e) {
        logger.error('Network/Fetch Error:', e)
      }
    }

    function onPlaybackToggled(data) {
      setIsPlaying(data.is_playing)
      if (player) {
        if (data.is_playing) player.resume()
        else player.pause()
      }
    }

    function onStopPlayer() {
      setCurrentTrack(null)
      setIsPlaying(false)
      setProgress(0)
      setDuration(0)
      if (player) player.pause()
    }

    function onDJCommentary(data) {
      if (data) {
        if (data.text) addLog(`DJ HAL: ${data.text}`)

        if (data.audio_url) {
          // Play server-side playing
          const audio = new Audio(data.audio_url);
          audio.volume = 1.0;

          // Duck music volume
          if (player) player.setVolume(0.2);

          audio.play().catch(e => logger.error("Audio playback error:", e));

          audio.onended = () => {
            // Restore volume
            if (player) player.setVolume(0.5);
          };
        } else if (data.text) {
          // Fallback to browser TTS if audio generation failed
          const utterance = new SpeechSynthesisUtterance(data.text);
          utterance.rate = 1.1;
          window.speechSynthesis.speak(utterance);
        }
      }
    }

    socket.on('connect', onConnect) // Need to bind connect explicitly if late bind
    socket.on('disconnect', onDisconnect)
    socket.on('room_state', onRoomState)
    socket.on('user_list_updated', onUserListUpdated)
    socket.on('play_track', onPlayTrack)
    socket.on('queue_updated', onQueueUpdated)
    socket.on('vibe_updated', onVibeUpdated)
    socket.on('playback_toggled', onPlaybackToggled)
    socket.on('stop_player', onStopPlayer)
    socket.on('dj_commentary', onDJCommentary) // NEW LISTENER

    // Check initial connection
    if (socket.connected) setIsConnected(true)

    return () => {
      socket.off('connect', onConnect)
      socket.off('disconnect', onDisconnect)
      socket.off('room_state', onRoomState)
      socket.off('user_list_updated', onUserListUpdated)
      socket.off('play_track', onPlayTrack)
      socket.off('queue_updated', onQueueUpdated)
      socket.off('vibe_updated', onVibeUpdated)
      socket.off('playback_toggled', onPlaybackToggled)
      socket.off('stop_player', onStopPlayer)
      socket.off('dj_commentary', onDJCommentary) // CLEANUP
    }
  }, [player, deviceId, token, userProfile])

  // Progress Interval for smoother UI
  useEffect(() => {
    if (!isPlaying || !currentTrack) return;
    const interval = setInterval(() => {
      setProgress(p => p + 1000)
    }, 1000)
    return () => clearInterval(interval)
  }, [isPlaying, currentTrack])

  // Update Page Title
  useEffect(() => {
    if (currentTrack) {
      document.title = `${currentTrack.name} • ${currentTrack.artist}`
    } else {
      document.title = 'VibeSync'
    }
  }, [currentTrack])

  const addLog = (msg) => {
    // console.log(msg)
  }

  const joinRoom = () => {
    if (roomId.trim()) {
      socket.emit('join_room', { room_id: roomId, user_profile: userProfile, token: token })
      setJoinedRoom(roomId)
    }
  }

  const leaveRoom = () => {
    if (player) player.pause()
    setIsPlaying(false)
    setJoinedRoom(null)
    setCurrentTrack(null)
    setQueue([])
    setHistory([])
    setRoomId('')
    window.history.replaceState({}, document.title, "/")
  }

  const copyLink = () => {
    const origin = window.location.origin;
    const url = `${origin}/?room=${joinedRoom}`;

    const copyToClipboard = (text) => {
      if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
      } else {
        let textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        return new Promise((res, rej) => {
          document.execCommand('copy') ? res() : rej();
          textArea.remove();
        });
      }
    }

    copyToClipboard(url)
      .then(() => alert('Room Link Copied! Send it to your friends.'))
      .catch(err => {
        console.error('Async: Could not copy text: ', err);
        prompt("Copy this link:", url);
      });
  }

  const handleSetVibe = (vibe) => {
    socket.emit('set_vibe', { room_id: joinedRoom, vibe_text: vibe })
  }

  const handleSearch = (e) => {
    const query = e.target.value
    setSearchQuery(query)

    if (searchTimeout.current) clearTimeout(searchTimeout.current)

    if (!query.trim()) {
      setSearchResults([])
      return
    }

    searchTimeout.current = setTimeout(async () => {
      try {
        const res = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=track&limit=5`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        if (data.tracks) {
          setSearchResults(data.tracks.items)
        }
      } catch (err) {
        console.error(err)
      }
    }, 500)
  }

  const addToQueue = (track) => {
    const trackData = {
      uri: track.uri,
      name: track.name,
      artist: track.artists.map(a => a.name).join(', '),
      image: track.album.images[0]?.url,
      duration_ms: track.duration_ms
    }
    socket.emit('add_to_queue', { room_id: joinedRoom, track: trackData })
    setSearchQuery('')
    setSearchQuery('')
    setSearchResults([])
  }

  const reQueue = (track) => {
    socket.emit('add_to_queue', { room_id: joinedRoom, track: track })
  }

  const skipSong = () => {
    socket.emit('skip_song', { room_id: joinedRoom })
  }

  const togglePlayback = () => {
    socket.emit('toggle_playback', { room_id: joinedRoom })
  }

  const removeFromQueue = (uuid) => {
    socket.emit('remove_from_queue', { room_id: joinedRoom, track_uuid: uuid })
  }

  const seek = (e) => {
    const newPos = parseInt(e.target.value);
    setProgress(newPos)
    if (player) player.seek(newPos)
  }

  const handleLogin = () => {
    window.location.href = `${BACKEND_URL}/login`
  }

  const handleLogout = () => {
    if (player) player.disconnect()
    setToken(null)
    setUserProfile(null)
    localStorage.removeItem('spotify_access_token')
    window.location.href = '/'
  }

  if (!token) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="app-container">
      {userProfile && userProfile.product !== 'premium' && (
        <div style={{
          backgroundColor: '#e74c3c',
          color: 'white',
          padding: '10px',
          textAlign: 'center',
          borderRadius: '8px',
          marginBottom: '1rem',
          marginTop: '1rem',
          fontWeight: 'bold'
        }}>
          ⚠️ Playback is limited: Spotify Premium is required to listen to music in this app. You can still manage the queue!
        </div>
      )}
      {!joinedRoom ? (
        <JoinRoom
          roomId={roomId}
          setRoomId={(val) => setRoomId(val.toLowerCase())}
          onJoin={joinRoom}
          onLogout={handleLogout}
          userProfile={userProfile}
        />
      ) : (
        <div className="dashboard">
          <RoomHeader
            roomName={joinedRoom}
            isConnected={isConnected}
            users={usersInRoom}
            onCopyLink={copyLink}
            onLeave={leaveRoom}
            userProfile={userProfile}
          />

          <div className="main-panel">
            <div className="left-column" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <Player
                currentTrack={currentTrack}
                isPlaying={isPlaying}
                progress={progress}
                duration={duration}
                onToggle={togglePlayback}
                onSkip={skipSong}
                onSeek={seek}
              />
              <VibeCheck activeVibe={activeVibe} onSetVibe={handleSetVibe} />
              <Search
                query={searchQuery}
                setQuery={handleSearch}
                results={searchResults}
                onAdd={addToQueue}
              />
            </div>


            <Queue
              queue={queue}
              history={history}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              users={usersInRoom}
              onRemove={removeFromQueue}
              onReQueue={reQueue}
            />
          </div>
        </div>
      )}
      <div style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        fontSize: '0.8rem',
        opacity: 0.7,
        color: 'rgba(255, 255, 255, 0.5)',
        zIndex: 9999,
        pointerEvents: 'none',
        userSelect: 'none'
      }}>
        v{VERSION}
      </div>
    </div>
  )
}

export default App
