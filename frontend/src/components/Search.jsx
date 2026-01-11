import '../styles/Search.css'


export default function Search({ query, setQuery, results, onAdd }) {
    return (
        <div className="card search-panel" style={{ position: 'relative' }}>
            <input
                placeholder="Search for a song..."
                value={query}
                onChange={setQuery}
                className="search-input"
            />
            {results.length > 0 && (
                <div className="search-results" style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: 0,
                    right: 0,
                    marginBottom: '10px',
                    background: '#1a1f26',
                    border: '1px solid rgba(80,80,80,0.5)',
                    borderRadius: '8px',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    zIndex: 100,
                    boxShadow: '0 -4px 20px rgba(0,0,0,0.5)'
                }}>
                    {results.map(track => (
                        <div key={track.id} className="result-item" onClick={() => onAdd(track)} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            padding: '10px',
                            cursor: 'pointer',
                            borderBottom: '1px solid rgba(255,255,255,0.05)'
                        }}>
                            <img src={track.album.images[2]?.url} alt="art" style={{ width: '40px' }} />
                            <div className="result-info" style={{ flex: 1, textAlign: 'left' }}>
                                <div className="r-name" style={{ fontWeight: 'bold' }}>{track.name}</div>
                                <div className="r-artist" style={{ fontSize: '0.8rem', opacity: 0.7 }}>{track.artists[0].name}</div>
                            </div>
                            <button className="add-btn" style={{ padding: '5px 10px' }}>+</button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
