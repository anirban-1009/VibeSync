import '../styles/JoinRoom.css'

export default function JoinRoom({ roomId, setRoomId, onJoin, onLogout, userProfile }) {
    return (
        <div className="card center-card">
            <img src="/favicon.png" alt="VibeSync Logo" style={{ width: '100px', margin: '0 auto 0rem', display: 'block' }} />
            <h1 style={{ marginTop: '0.2rem' }}>VibeSync</h1>

            {userProfile && (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.05)', padding: '8px 16px', borderRadius: '50px' }}>
                    <div style={{ width: '32px', height: '32px', borderRadius: '50%', overflow: 'hidden', background: '#333', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {userProfile.images && userProfile.images.length > 0 ? (
                            <img src={userProfile.images[0].url} alt={userProfile.display_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                            <span style={{ fontSize: '14px', fontWeight: 'bold' }}>{(userProfile.display_name || 'U')[0]}</span>
                        )}
                    </div>
                    <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{userProfile.display_name}</span>
                </div>
            )}

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
            <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#666', cursor: 'pointer', textDecoration: 'underline' }} onClick={onLogout}>
                Switch Spotify Account
            </p>
        </div>
    )
}
