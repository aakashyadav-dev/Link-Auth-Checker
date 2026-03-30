import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BiometricsModule = ({ sessionId }) => {
    const [mouseMovements, setMouseMovements] = useState([]);
    const [keystrokes, setKeystrokes] = useState([]);
    const [verificationResult, setVerificationResult] = useState(null);
    const [tracking, setTracking] = useState(true);

    useEffect(() => {
        if (!tracking) return;

        // Track mouse movements
        const handleMouseMove = (e) => {
            setMouseMovements(prev => {
                const newMovement = {
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                };
                return [...prev.slice(-50), newMovement];
            });
        };

        // Track keystrokes
        const handleKeyDown = (e) => {
            setKeystrokes(prev => {
                const newKeystroke = {
                    key: e.key,
                    press_time: Date.now()
                };
                return [...prev.slice(-50), newKeystroke];
            });
        };

        const handleKeyUp = (e) => {
            setKeystrokes(prev => {
                const lastKeystroke = prev[prev.length - 1];
                if (lastKeystroke && lastKeystroke.key === e.key && !lastKeystroke.release_time) {
                    lastKeystroke.release_time = Date.now();
                }
                return [...prev];
            });
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [tracking]);

    const verifyIdentity = async () => {
        try {
            const response = await axios.post('http://localhost:5001/biometrics/verify', {
                session_id: sessionId,
                behavior: {
                    mouse: mouseMovements,
                    keystroke: keystrokes
                }
            });
            setVerificationResult(response.data);
        } catch (error) {
            console.error('Verification error:', error);
        }
    };

    const getProfile = async () => {
        try {
            const response = await axios.get(`http://localhost:5001/behavioral_analytics/${sessionId}`);
            setVerificationResult(response.data.biometric_profile);
        } catch (error) {
            console.error('Get profile error:', error);
        }
    };

    return (
        <div className="biometrics-container">
            <h3>Behavioral Biometrics</h3>
            
            <div className="tracking-status">
                <label>
                    <input
                        type="checkbox"
                        checked={tracking}
                        onChange={(e) => setTracking(e.target.checked)}
                    />
                    Enable Behavior Tracking
                </label>
            </div>

            <div className="biometrics-stats">
                <div className="stat">
                    <label>Mouse Movements:</label>
                    <span>{mouseMovements.length}</span>
                </div>
                <div className="stat">
                    <label>Keystrokes:</label>
                    <span>{keystrokes.length}</span>
                </div>
            </div>

            <div className="biometrics-actions">
                <button onClick={verifyIdentity}>Verify Identity</button>
                <button onClick={getProfile}>View Profile</button>
            </div>

            {verificationResult && (
                <div className="verification-result">
                    <h4>Verification Result</h4>
                    <div className={`verification-status ${verificationResult.verified ? 'verified' : 'not-verified'}`}>
                        {verificationResult.verified ? '✅ Verified' : '❌ Not Verified'}
                    </div>
                    <div className="confidence">
                        Confidence: {(verificationResult.confidence * 100).toFixed(1)}%
                    </div>
                    {verificationResult.reason && (
                        <div className="reason">Reason: {verificationResult.reason}</div>
                    )}
                </div>
            )}

            <style jsx>{`
                .biometrics-container {
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 8px;
                }
                .tracking-status {
                    margin-bottom: 15px;
                }
                .biometrics-stats {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 15px;
                }
                .stat {
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }
                .biometrics-actions {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                }
                .biometrics-actions button {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .verification-result {
                    padding: 15px;
                    background: white;
                    border-radius: 4px;
                }
                .verification-status {
                    font-size: 1.2em;
                    margin: 10px 0;
                }
                .verification-status.verified {
                    color: #28a745;
                }
                .verification-status.not-verified {
                    color: #dc3545;
                }
                .confidence {
                    font-weight: bold;
                }
                .reason {
                    margin-top: 10px;
                    color: #666;
                }
            `}</style>
        </div>
    );
};

export default BiometricsModule;