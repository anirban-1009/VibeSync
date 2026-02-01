
import '../styles/Player.css';

export default function Player({ currentTrack, isPlaying, progress, duration, onToggle, onSkip, onSeek, repeatMode, onRepeat, volume, onVolume }) {
    const formatTime = (ms) => {
        const minutes = Math.floor(ms / 60000);
        const seconds = ((ms % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    return (
        <div className="card now-playing" style={{ textAlign: 'center', alignItems: 'center' }}>
            {currentTrack ? (
                <>
                    <img src={currentTrack.image} alt="Album Art" className="album-art" style={{ width: '250px', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }} />
                    <div className="track-info" style={{ margin: '1rem 0' }}>
                        <h2 style={{ margin: '0', fontSize: '1.5rem' }}>{currentTrack.name}</h2>
                        <p style={{ margin: '0.2rem 0', opacity: 0.7 }}>{currentTrack.artist}</p>

                        {/* Added By logic */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', marginTop: '8px', fontSize: '0.8rem', opacity: 0.8 }}>
                            <span>Added by</span>
                            {currentTrack.added_by === 'system' ? (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--primary-color)', fontWeight: 'bold' }}>
                                    <svg style={{ width: '16px', height: '16px', fill: 'currentColor' }} viewBox="0 0 24 24">
                                        <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H19A2,2 0 0,1 21,9V20A2,2 0 0,1 19,22H5A2,2 0 0,1 3,20V9A2,2 0 0,1 5,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M7.5,13A1.5,1.5 0 0,0 6,14.5A1.5,1.5 0 0,0 7.5,16A1.5,1.5 0 0,0 9,14.5A1.5,1.5 0 0,0 7.5,13M16.5,13A1.5,1.5 0 0,0 15,14.5A1.5,1.5 0 0,0 16.5,16A1.5,1.5 0 0,0 18,14.5A1.5,1.5 0 0,0 16.5,13M12,17A3,3 0 0,0 9.13,15.76L9.6,17.65C10.68,17.38 11.83,17.62 12.68,18.27L13.82,16.8C13.3,16.39 12.67,16.12 12,16V17Z" />
                                    </svg>
                                    AI DJ
                                </div>
                            ) : (
                                <span style={{ fontWeight: 'bold' }}>{currentTrack.added_by_name || 'Anonymous'}</span>
                            )}
                        </div>
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

                        {/* Repeat Button */}
                        <button
                            onClick={onRepeat}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                cursor: 'pointer',
                                opacity: repeatMode === 'off' ? 0.4 : 1,
                                position: 'relative',
                                color: repeatMode === 'off' ? 'inherit' : 'var(--primary-color)'
                            }}
                            title={`Repeat: ${repeatMode}`}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z" />
                            </svg>
                            {repeatMode === 'track' && (
                                <span style={{
                                    position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                                    fontSize: '10px', fontWeight: 'bold'
                                }}>1</span>
                            )}
                        </button>

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

                        {/* Skip Button */}
                        <button onClick={onSkip} style={{ background: 'transparent', border: 'none', cursor: 'pointer', opacity: 0.8 }} title="Skip Track">
                            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" /></svg>
                        </button>

                        {/* Volume Control */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginLeft: '10px' }}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ opacity: 0.6 }}>
                                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
                            </svg>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={volume}
                                onChange={(e) => onVolume(parseInt(e.target.value))}
                                style={{ width: '60px', accentColor: 'var(--primary-color)' }}
                            />
                        </div>

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
