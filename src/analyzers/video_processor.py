"""
This module contains the video processing logic for the BikeFit application.
"""
import cv2
import mediapipe as mp
import time
from .angle_calculator import calculate_angle

def process_media(source, pose, display=True):
    """
    Processes a video source (from file or camera) to extract bike fit angles.

    Args:
        source: The video source (camera index or file path).
        pose: The MediaPipe pose object.
        display (bool): Whether to display the video feed with landmarks.

    Returns:
        A tuple containing (knee_angles, hip_angles, timestamps).
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Could not open video source: {source}")
        return [], [], []

    knee_angles = []
    hip_angles = []
    timestamps = []
    start_time = time.time()

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        current_time = time.time() - start_time

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        image.flags.writeable = True


        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            hip = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value].y]
            shoulder = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y]

            # Calculate angles
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)
        
            knee_angles.append(round(knee_angle, 3))
            hip_angles.append(round(hip_angle, 3))
            timestamps.append(current_time)

            if display:
                # Draw landmarks and angles on the image
                h, w, _ = image.shape
                hip_px = (int(hip[0] * w), int(hip[1] * h))
                knee_px = (int(knee[0] * w), int(knee[1] * h))
                ankle_px = (int(ankle[0] * w), int(ankle[1] * h))
                shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))

                mp.solutions.drawing_utils.draw_landmarks(
                    image, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
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

                cv2.imshow('BikeFit Analysis', image)

                if cv2.waitKey(5) & 0xFF == 27: # Press ESC to stop
                    break
    
    cap.release()
    if display:
        cv2.destroyAllWindows()
        # Add this to ensure window closes on all systems
        for i in range(5):
            cv2.waitKey(1)

    return knee_angles, hip_angles, timestamps
