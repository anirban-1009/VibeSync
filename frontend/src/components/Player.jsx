
import '../styles/Player.css';

export default function Player({ currentTrack, isPlaying, progress, duration, onToggle, onSkip, onSeek }) {
    const formatTime = (ms) => {
        const minutes = Math.floor(ms / 60000);
        const seconds = ((ms % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    return (
        <div className="card now-playing" style={{ textAlign: 'center' }}>
            {currentTrack ? (
                <>
                    <img src={currentTrack.image} alt="Album Art" className="album-art" style={{ width: '250px', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }} />
                    <div className="track-info" style={{ margin: '1rem 0' }}>
                        <h2 style={{ margin: '0', fontSize: '1.5rem' }}>{currentTrack.name}</h2>
                        <p style={{ margin: '0.2rem 0', opacity: 0.7 }}>{currentTrack.artist}</p>
                    </div>

                    <div className="progress-container">
                        <span className="time-display">{formatTime(progress)}</span>
                        <input
                            type="range"
                            min="0"
                            max={duration || currentTrack.duration_ms || 100}
                            value={progress}
                            onChange={onSeek}
                            className="progress-slider"
                            style={{
                                background: `linear-gradient(to right, var(--primary-color) ${(progress / (duration || currentTrack.duration_ms || 1)) * 100}%, rgba(255,255,255,0.1) ${(progress / (duration || currentTrack.duration_ms || 1)) * 100}%)`
                            }}
                        />
                        <span className="time-display">{formatTime(duration || currentTrack.duration_ms || 0)}</span>
                    </div>

                    <div className="controls" style={{ display: 'flex', gap: '20px', justifyContent: 'center', alignItems: 'center', marginTop: '1rem' }}>
                        <button
                            onClick={onToggle}
                            style={{
                                width: '60px',
                                height: '60px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: 0,
                                background: 'var(--primary-color)',
                                border: 'none',
                                cursor: 'pointer'
                            }}
                        >
                            {isPlaying ? (
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M11 19V5h-4v14h4zm6-14h-4v14h4V5z" /></svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                            )}
                        </button>
                        <button onClick={onSkip} style={{ background: 'transparent', border: 'none', cursor: 'pointer', opacity: 0.8 }} title="Skip Track">
                            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" /></svg>
                        </button>
                    </div>
                </>
            ) : (
                <div className="idle-state">
                    <div className="pulse-ring"></div>
                    <h2>Room is Idle</h2>
                    <p>Queue a song to start the party</p>
                </div>
            )}
        </div>
    )
}
