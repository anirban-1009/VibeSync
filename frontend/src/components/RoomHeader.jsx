import '../styles/RoomHeader.css'


export default function RoomHeader({ roomName, isConnected, users, onCopyLink, onLeave }) {
    return (
        <header className="room-header">
            <div className="center-header">
                <h1 style={{ margin: 0, marginBottom: '0.5rem', fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                    {roomName}
                    <span className={`status-badge ${isConnected ? '' : 'disconnected'}`} style={{ fontSize: '0.9rem', marginLeft: '15px', verticalAlign: 'middle', position: 'relative', top: '-4px' }}>
                        {isConnected ? 'ONLINE' : 'OFFLINE'}
                    </span>
                </h1>

                <div className="users-list">
                    {users.map((u, i) => (
                        <div key={i} className="user-avatar-container">
                            <div className="user-avatar">
                                {u.image ? <img src={u.image} alt={u.name} style={{ width: '100%', height: '100%' }} /> : u.name[0]}
                            </div>
                            <div className="user-tooltip">
                                {u.name}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="header-controls">
                <button onClick={onCopyLink} style={{ background: 'rgba(255,255,255,0.1)' }}>Share</button>
                <button onClick={onLeave} style={{ background: 'rgba(255,50,50,0.2)', borderColor: 'rgba(255,50,50,0.4)', color: '#ffaaaa' }}>Exit</button>
            </div>
        </header>
    )
}
