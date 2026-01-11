import '../styles/Login.css'


export default function Login({ onLogin }) {
    return (
        <div className="card">
            <img src="/favicon.png" alt="VibeSync Logo" style={{ width: '100px', margin: '0 auto 0rem', display: 'block' }} />
            <h1 style={{ marginTop: '0.2rem' }}>VibeSync</h1>
            <button onClick={onLogin} className="spotify-btn" style={{ background: '#1DB954', borderColor: '#1DB954', color: 'white', fontSize: '1.2rem', padding: '10px 20px', borderRadius: '50px' }}>
                Login with Spotify
            </button>
        </div>
    )
}
