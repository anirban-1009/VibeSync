import '../styles/JoinRoom.css'

export default function JoinRoom({ roomId, setRoomId, onJoin }) {
    return (
        <div className="card center-card">
            <img src="/favicon.png" alt="VibeSync Logo" style={{ width: '100px', margin: '0 auto 0rem', display: 'block' }} />
            <h1 style={{ marginTop: '0.2rem' }}>VibeSync</h1>
            <div className="join-controls" style={{ display: 'flex', gap: '10px' }}>
                <input
                    placeholder="Enter Room ID..."
                    value={roomId}
                    onChange={e => setRoomId(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && onJoin()}
                    style={{ flex: 1 }}
                />
                <button onClick={onJoin}>Join</button>
            </div>
        </div>
    )
}
