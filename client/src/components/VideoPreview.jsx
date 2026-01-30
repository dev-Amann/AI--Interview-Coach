import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import { mediaPipeHelper } from '../utils/MediaPipeHelper';
import { Camera, Eye, Brain, Compass } from 'lucide-react';

const VideoPreview = ({ onBehaviorAlert }) => {
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const [trackingStatus, setTrackingStatus] = useState("Initializing AI...");
    const [gazeStatus, setGazeStatus] = useState("Checking...");
    const [emotionStatus, setEmotionStatus] = useState("Neutral");
    const [headPoseStatus, setHeadPoseStatus] = useState("Centered");
    const requestRef = useRef(null);
    const lastVideoTimeRef = useRef(-1);
    const alertCooldownRef = useRef({});

    useEffect(() => {
        const initAI = async () => {
            await mediaPipeHelper.initialize();
            setTrackingStatus("AI Ready");
        };
        initAI();

        return () => {
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
        };
    }, []);

    // Throttle alerts to prevent spam (one alert per type per 5 seconds)
    const sendAlert = (type, message) => {
        const now = Date.now();
        if (!alertCooldownRef.current[type] || now - alertCooldownRef.current[type] > 5000) {
            alertCooldownRef.current[type] = now;
            if (onBehaviorAlert) onBehaviorAlert(message);
        }
    };

    // Head Pose Detection using facial landmarks (nose position relative to face)
    const analyzeHeadPose = (landmarks) => {
        if (!landmarks || landmarks.length === 0) {
            return "Unknown";
        }

        const face = landmarks[0];

        try {
            const noseTip = face[1];
            const leftEye = face[33];
            const rightEye = face[263];
            const forehead = face[10];
            const chin = face[152];

            // Calculate face center
            const faceCenterX = (leftEye.x + rightEye.x) / 2;
            const faceCenterY = (forehead.y + chin.y) / 2;

            // Check horizontal deviation (left/right)
            const horizontalOffset = noseTip.x - faceCenterX;
            // Check vertical deviation (up/down)  
            const verticalOffset = noseTip.y - faceCenterY;

            if (horizontalOffset > 0.02) {
                sendAlert("headpose", "ALERT: Head turned left");
                return "← Turned Left";
            } else if (horizontalOffset < -0.02) {
                sendAlert("headpose", "ALERT: Head turned right");
                return "Turned Right →";
            } else if (verticalOffset > 0.04) {
                sendAlert("headpose", "ALERT: Looking down");
                return "↓ Looking Down";
            } else if (verticalOffset < -0.02) {
                sendAlert("headpose", "ALERT: Looking up");
                return "↑ Looking Up";
            }

            return "Centered ✓";
        } catch (e) {
            return "Centered ✓";
        }
    };

    // Gaze Detection using iris landmarks
    const analyzeGaze = (landmarks) => {
        if (!landmarks || landmarks.length === 0) return "Unknown";

        const face = landmarks[0];

        // MediaPipe iris landmarks: Left eye (468-472), Right eye (473-477)
        // Center of iris vs eye corners can estimate gaze
        try {
            // Left iris center (landmark 468)
            const leftIris = face[468];
            // Left eye corners (landmarks 33 and 133)
            const leftEyeLeft = face[33];
            const leftEyeRight = face[133];

            if (leftIris && leftEyeLeft && leftEyeRight) {
                const eyeWidth = Math.abs(leftEyeRight.x - leftEyeLeft.x);
                const irisPosition = (leftIris.x - leftEyeLeft.x) / eyeWidth;

                // irisPosition: 0 = looking right, 0.5 = center, 1 = looking left
                if (irisPosition < 0.35) {
                    sendAlert("gaze", "ALERT: Looking away from screen");
                    return "Looking Away";
                } else if (irisPosition > 0.65) {
                    sendAlert("gaze", "ALERT: Looking away from screen");
                    return "Looking Away";
                }
            }
        } catch (e) {
            // Landmark not available
        }

        return "Focused";
    };

    // Emotion Detection using face blendshapes
    const analyzeEmotion = (blendshapes) => {
        if (!blendshapes || blendshapes.length === 0) return "Neutral";

        const shapes = blendshapes[0]?.categories || [];

        // Create a map for easier access
        const shapeMap = {};
        shapes.forEach(s => {
            shapeMap[s.categoryName] = s.score;
        });

        // Detect emotions based on blendshape combinations
        const mouthSmileLeft = shapeMap['mouthSmileLeft'] || 0;
        const mouthSmileRight = shapeMap['mouthSmileRight'] || 0;
        const browDownLeft = shapeMap['browDownLeft'] || 0;
        const browDownRight = shapeMap['browDownRight'] || 0;
        const browInnerUp = shapeMap['browInnerUp'] || 0;
        const mouthFrownLeft = shapeMap['mouthFrownLeft'] || 0;
        const mouthFrownRight = shapeMap['mouthFrownRight'] || 0;
        const jawOpen = shapeMap['jawOpen'] || 0;

        const smileScore = (mouthSmileLeft + mouthSmileRight) / 2;
        const frownScore = (browDownLeft + browDownRight + mouthFrownLeft + mouthFrownRight) / 4;
        const surpriseScore = browInnerUp + jawOpen;

        if (smileScore > 0.4) {
            return "😊 Confident";
        } else if (frownScore > 0.3) {
            return "😟 Concerned";
        } else if (surpriseScore > 0.6) {
            return "😮 Surprised";
        } else if (browInnerUp > 0.3 && frownScore < 0.2) {
            return "🤔 Thinking";
        }

        return "😐 Neutral";
    };

    const detectBehavior = (results) => {
        if (!results || !results.faceLandmarks || results.faceLandmarks.length === 0) {
            setTrackingStatus("No Face Detected!");
            setGazeStatus("--");
            setEmotionStatus("--");
            setHeadPoseStatus("--");
            sendAlert("noface", "WARNING: No face detected in frame.");
            return;
        }

        if (results.faceLandmarks.length > 1) {
            setTrackingStatus("Multiple Faces!");
            sendAlert("multiface", "WARNING: Multiple people detected.");
            return;
        }

        // Face is present
        setTrackingStatus("Monitoring Active");

        // Analyze Head Pose (now uses landmarks)
        const pose = analyzeHeadPose(results.faceLandmarks);
        setHeadPoseStatus(pose);

        // Analyze Gaze
        const gaze = analyzeGaze(results.faceLandmarks);
        setGazeStatus(gaze);

        // Analyze Emotion
        const emotion = analyzeEmotion(results.faceBlendshapes);
        setEmotionStatus(emotion);
    };

    const captureFrame = () => {
        if (
            webcamRef.current &&
            webcamRef.current.video &&
            webcamRef.current.video.readyState === 4
        ) {
            const video = webcamRef.current.video;
            const videoTime = video.currentTime;

            if (videoTime !== lastVideoTimeRef.current) {
                lastVideoTimeRef.current = videoTime;
                const results = mediaPipeHelper.detectForVideo(video, performance.now());
                detectBehavior(results);
            }
        }
        requestRef.current = requestAnimationFrame(captureFrame);
    };

    const onUserMedia = () => {
        setIsCameraReady(true);
        requestRef.current = requestAnimationFrame(captureFrame);
    };

    return (
        <div className="relative rounded-2xl overflow-hidden bg-black shadow-lg border border-gray-800 aspect-video">
            <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                    width: 320,
                    height: 240,
                    facingMode: "user"
                }}
                onUserMedia={onUserMedia}
                className="absolute top-0 left-0 w-full h-full object-cover opacity-80"
            />

            <canvas
                ref={canvasRef}
                width={320}
                height={240}
                className="absolute top-0 left-0 w-full h-full object-cover opacity-50 pointer-events-none"
            />

            {/* Status Overlay - Enhanced */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-3 space-y-1">
                {/* Main Status */}
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${trackingStatus.includes("Active") ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
                    <span className="text-xs text-white font-semibold">{trackingStatus}</span>
                </div>

                {/* Detailed Indicators */}
                <div className="grid grid-cols-3 gap-2 text-[10px]">
                    <div className="flex items-center gap-1 text-gray-300">
                        <Eye className="w-3 h-3" />
                        <span>{gazeStatus}</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-300">
                        <Brain className="w-3 h-3" />
                        <span>{emotionStatus}</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-300">
                        <Compass className="w-3 h-3" />
                        <span>{headPoseStatus}</span>
                    </div>
                </div>
            </div>

            {!isCameraReady && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
                    <div className="text-center">
                        <Camera className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                        <p className="text-gray-400 text-sm">Starting Camera...</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoPreview;
