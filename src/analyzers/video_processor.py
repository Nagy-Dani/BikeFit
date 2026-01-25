"""
This module contains the video processing logic for the BikeFit application.
"""
import cv2
import mediapipe as mp
import time
from .angle_calculator import calculate_angle

class BikeFitProcessor:
    """
    Handles the MediaPipe Pose estimation and angle calculations for a single frame.
    Designed to be used within a GUI loop or video processing thread.
    """
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, image):
        """
        Processes a single frame: detects landmarks, calculates angles, and draws overlays.
        
        Args:
            image: The input image (BGR format from OpenCV).
            
        Returns:
            processed_image: Image with landmarks drawn.
            data: Dictionary containing calculated angles (knee, hip) and raw landmarks, or None if no pose detected.
        """
        # Convert to RGB for MediaPipe
        # optimization: pass by reference flags
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        image.flags.writeable = True

        data = None

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

            # Calculate angles
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)
        
            data = {
                'knee_angle': round(knee_angle, 3),
                'hip_angle': round(hip_angle, 3),
                'landmarks': results.pose_landmarks
            }

            # Draw visualization
            self._draw_overlays(image, results.pose_landmarks, hip, knee, ankle, shoulder, knee_angle, hip_angle)

        return image, data

    def _draw_overlays(self, image, landmarks, hip, knee, ankle, shoulder, knee_angle, hip_angle):
        """Helper to draw lines and text on the image."""
        h, w, _ = image.shape
        hip_px = (int(hip[0] * w), int(hip[1] * h))
        knee_px = (int(knee[0] * w), int(knee[1] * h))
        ankle_px = (int(ankle[0] * w), int(ankle[1] * h))
        shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))

        self.mp_drawing.draw_landmarks(
            image, landmarks, self.mp_pose.POSE_CONNECTIONS
        )

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (0, 255, 0)
        thickness = 2

        cv2.putText(image, f"Knee: {knee_angle:.1f}", (knee_px[0] + 10, knee_px[1]), font, font_scale, color, thickness)
        cv2.putText(image, f"Hip: {hip_angle:.1f}", (hip_px[0] + 10, hip_px[1]), font, font_scale, color, thickness)
        
        cv2.line(image, hip_px, knee_px, color, thickness)
        cv2.line(image, knee_px, ankle_px, color, thickness)
        cv2.line(image, shoulder_px, hip_px, color, thickness)

    def close(self):
        self.pose.close()

def process_media(source, pose=None, display=True):
    """
    Legacy wrapper for backward compatibility using the new BikeFitProcessor.
    Args:
        source: Video source.
        pose: Ignored in this new version as Processor handles it.
        display: Whether to show cv2.imshow (blocking).
    """
    processor = BikeFitProcessor()
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source: {source}")
        return [], [], []

    knee_angles = []
    hip_angles = []
    timestamps = []
    start_time = time.time()
    
    is_video_file = isinstance(source, str)

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            if is_video_file:
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            else:
                current_time = time.time() - start_time

            processed_image, data = processor.process_frame(image)

            if data:
                knee_angles.append(data['knee_angle'])
                hip_angles.append(data['hip_angle'])
                timestamps.append(current_time)

            if display:
                cv2.imshow('BikeFit Analysis', processed_image)
                if cv2.waitKey(5) & 0xFF == 27: # Press ESC to stop
                    break
    finally:
        cap.release()
        processor.close()
        if display:
            cv2.destroyAllWindows()
            for i in range(5): cv2.waitKey(1)

    return knee_angles, hip_angles, timestamps