import { QRCodeSVG } from 'qrcode.react';
import { useState } from 'react';
import '../styles/App.css';

const ShareModal = ({ isOpen, onClose, roomUrl }) => {
    const [copied, setCopied] = useState(false);

    if (!isOpen) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(roomUrl).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const handleNativeShare = async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'VibeSync Party',
                    text: 'Join my VibeSync room and add some tracks!',
                    url: roomUrl
                });
            } catch (err) {
                console.log('Error sharing:', err);
            }
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose} style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(5px)'
        }}>
            <div className="modal-content tile" onClick={e => e.stopPropagation()} style={{
                maxWidth: '400px',
                width: '90%',
                padding: '2rem',
                textAlign: 'center',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
            }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '15px',
                        right: '15px',
                        background: 'transparent',
                        border: 'none',
                        color: 'white',
                        fontSize: '1.5rem',
                        cursor: 'pointer',
                        padding: 0,
                        lineHeight: 1
                    }}
                >
                    &times;
                </button>

                <h2 style={{ marginTop: 0 }}>Join the Party!</h2>

                <div style={{ background: 'white', padding: '15px', borderRadius: '12px', width: 'fit-content', margin: '0 auto' }}>
                    <QRCodeSVG value={roomUrl} size={180} />
                </div>

                <p style={{ opacity: 0.7, fontSize: '0.9rem', margin: 0 }}>
                    Scan to join from your phone
                </p>

                <div className="input-with-button" style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '5px', borderRadius: '8px' }}>
                    <input
                        type="text"
                        readOnly
                        value={roomUrl}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'white',
                            flex: 1,
                            padding: '0 10px',
                            fontSize: '0.8rem',
                            textOverflow: 'ellipsis'
                        }}
                    />
                    <button onClick={handleCopy} className="button secondary" style={{ minWidth: '80px' }}>
                        {copied ? 'Copied!' : 'Copy'}
                    </button>
                </div>

                {navigator.share && (
                    <button onClick={handleNativeShare} className="button primary" style={{ width: '100%' }}>
                        Share via...
                    </button>
                )}
            </div>
        </div>
    );
};

export default ShareModal;
