import { useState } from 'react'
import '../styles/App.css'

function VibeCheck({ onSetVibe, activeVibe }) {
    const [inputValue, setInputValue] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (inputValue.trim()) {
            onSetVibe(inputValue)
            // Optionally clear, or keep it to show what was typed
            setInputValue('')
        }
    }

    const suggestions = ["Chill", "Party", "Focus", "90s Hip Hop", "Techno Bunker"]

    return (
        <div className="vibe-check tile">
            <h3>Vibe Check ✨</h3>
            <p className="description">Tell the AI DJ what mood to set for auto-queued tracks.</p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <input
                    type="text"
                    className="search-input"
                    placeholder="e.g. 'Chill lo-fi for studying'..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                />
                <button type="submit" className="button primary">Set</button>
            </form>

            <div className="tags">
                {suggestions.map(s => (
                    <span
                        key={s}
                        className="tag"
                        onClick={() => setInputValue(s)}
                        style={{ cursor: 'pointer', fontSize: '0.8rem', padding: '4px 8px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', marginRight: '5px' }}
                    >
                        {s}
                    </span>
                ))}
            </div>

            {activeVibe && (
                <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#4CAF50' }}>
                    <strong>Current Vibe:</strong> {activeVibe}
                </div>
            )}
        </div>
    )
}

export default VibeCheck
