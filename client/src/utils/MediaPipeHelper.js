import { FilesetResolver, FaceLandmarker } from "@mediapipe/tasks-vision";

class MediaPipeHelper {
    constructor() {
        this.faceLandmarker = null;
        this.runningMode = "VIDEO";
    }

    async initialize() {
        if (this.faceLandmarker) return;

        const vision = await FilesetResolver.forVisionTasks(
            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
        );

        this.faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task`,
                delegate: "GPU",
            },
            outputFaceBlendshapes: true,
            outputFacialTransformationMatrixs: true,
            runningMode: this.runningMode,
            numFaces: 3,  // Detect up to 3 faces for cheating detection
        });

        console.log("MediaPipe FaceLandmarker loaded successfully");
    }

    detectForVideo(video, startTimeMs) {
        if (!this.faceLandmarker) return null;
        return this.faceLandmarker.detectForVideo(video, startTimeMs);
    }
}

// Export a singleton instance
export const mediaPipeHelper = new MediaPipeHelper();
