import '../styles/Queue.css'


export default function Queue({ queue, history, activeTab, setActiveTab, users, onRemove, onReQueue }) {

    const getUserInfo = (userId) => {
        return users.find(u => u.id === userId) || { name: '?', image: null }
    }

    const renderItem = (track, i, isHistory = false) => {
        const addedByUser = getUserInfo(track.added_by)
        return (
            <div key={i} className={`queue-item ${isHistory ? 'history-item' : ''}`} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: isHistory ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.05)',
                padding: '8px',
                borderRadius: '6px',
                opacity: isHistory ? 0.7 : 1
            }}>
                <img src={track.image} alt="art" style={{ width: '40px', height: '40px', borderRadius: '4px', filter: isHistory ? 'grayscale(50%)' : 'none' }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="q-name" style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{track.name}</div>
                    <div className="q-artist" style={{ fontSize: '0.8rem', opacity: 0.7 }}>{track.artist}</div>
                </div>

                {/* Added By Avatar */}
                {addedByUser && (
                    <div title={`Added by ${addedByUser.name}`}>
                        {addedByUser.image ? (
                            <img src={addedByUser.image} className="added-by-avatar" alt={addedByUser.name} style={{ opacity: isHistory ? 0.6 : 1 }} />
                        ) : (
                            <div className="added-by-initial">{addedByUser.name?.[0]}</div>
                        )}
                    </div>
                )}

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
