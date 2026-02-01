import '../styles/Queue.css'


export default function Queue({ queue, history, activeTab, setActiveTab, users, onRemove, onReQueue }) {



    const renderItem = (track, i, isHistory = false) => {
        // Use embedded info if available, otherwise fallback to finding active user
        let addedByName = track.added_by_name || '?'
        let addedByImage = track.added_by_image || null
        let isAi = track.added_by === 'system'

        if (isAi) {
            addedByName = 'AI DJ'
        } else if (addedByName === '?' && track.added_by) {
            const foundUser = users.find(u => u.id === track.added_by)
            if (foundUser) {
                addedByName = foundUser.name
                addedByImage = foundUser.image
            }
        }

        return (
            <div key={i} className={`queue-item ${isHistory ? 'history-item' : ''}`} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: isHistory ? 'rgba(255,255,255,0.02)' : (isAi ? 'linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(100,200,255,0.05) 100%)' : 'rgba(255,255,255,0.05)'),
                padding: '8px',
                borderRadius: '6px',
                opacity: isHistory ? 0.7 : 1,
                borderLeft: isAi ? '3px solid var(--primary-color)' : '3px solid transparent'
            }}>
                <img src={track.image} alt="art" style={{ width: '40px', height: '40px', borderRadius: '4px', filter: isHistory ? 'grayscale(50%)' : 'none' }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="q-name" style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{track.name}</div>
                    <div className="q-artist" style={{ fontSize: '0.8rem', opacity: 0.7 }}>{track.artist}</div>
                </div>

                {/* Added By Avatar */}
                <div title={`Added by ${addedByName}`}>
                    {isAi ? (
                        <div style={{
                            width: '30px', height: '30px', borderRadius: '50%',
                            background: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 0 10px var(--primary-color)'
                        }}>
                            <svg style={{ width: '20px', height: '20px', fill: '#000' }} viewBox="0 0 24 24">
                                <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H19A2,2 0 0,1 21,9V20A2,2 0 0,1 19,22H5A2,2 0 0,1 3,20V9A2,2 0 0,1 5,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M7.5,13A1.5,1.5 0 0,0 6,14.5A1.5,1.5 0 0,0 7.5,16A1.5,1.5 0 0,0 9,14.5A1.5,1.5 0 0,0 7.5,13M16.5,13A1.5,1.5 0 0,0 15,14.5A1.5,1.5 0 0,0 16.5,16A1.5,1.5 0 0,0 18,14.5A1.5,1.5 0 0,0 16.5,13M12,17A3,3 0 0,0 9.13,15.76L9.6,17.65C10.68,17.38 11.83,17.62 12.68,18.27L13.82,16.8C13.3,16.39 12.67,16.12 12,16V17Z" />
                            </svg>
                        </div>
                    ) : addedByImage ? (
                        <img src={addedByImage} className="added-by-avatar" alt={addedByName} style={{ opacity: isHistory ? 0.6 : 1 }} />
                    ) : (
                        <div className="added-by-initial">{addedByName?.[0]}</div>
                    )}
                </div>

                {isHistory ? (
                    <button
                        onClick={() => onReQueue(track)}
                        style={{ padding: '4px 8px', fontSize: '1.2rem', lineHeight: 1, background: 'transparent', border: 'none', opacity: 0.5, cursor: 'pointer', marginLeft: '5px', color: 'var(--primary-color)' }}
                        title="Add to Queue"
                    >+</button>
                ) : (
                    <button
                        onClick={() => onRemove(track.uuid)}
                        style={{ padding: '4px 8px', fontSize: '1.2rem', lineHeight: 1, background: 'transparent', border: 'none', opacity: 0.5, cursor: 'pointer', marginLeft: '5px' }}
                        title="Remove from queue"
                    >×</button>
                )}
            </div>
        )
    }

    return (
        <div className="card queue-panel" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column' }}>
            <div className="queue-header">
                <div className="queue-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
                        onClick={() => setActiveTab('queue')}
                    >
                        Up Next
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        History
                    </button>
                </div>
            </div>

            {activeTab === 'queue' ? (
                queue.length === 0 ? (
                    <p className="empty-queue" style={{ opacity: 0.5 }}>The queue is empty. Add a song below!</p>
                ) : (
                    <div className="queue-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {queue.map((track, i) => renderItem(track, i, false))}
                    </div>
                )
            ) : (
                history.length === 0 ? (
                    <p className="empty-queue" style={{ opacity: 0.5 }}>No songs played yet.</p>
                ) : (
                    <div className="queue-list history-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {history.map((track, i) => renderItem(track, i, true))}
                    </div>
                )
            )}
        </div>
    )
}
