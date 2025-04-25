import cv2
import mediapipe as mp
import math
import numpy as np
import csv 
import pandas as pd
import os
import User
import angle_calculator
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog




def clear_terminal():
    # Check the operating system and execute the appropriate command
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac
        os.system('clear')
        
def to_csv(knee_angles, hip_angles):
    csv_filename = 'test.csv'
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file) 
        writer.writerow(['Measurement', 'Knee Angle', 'Hip Angle'])
        for i, (k_angle, h_angle) in enumerate(zip(knee_angles, hip_angles)):
            writer.writerow([i+1, k_angle, h_angle])

def angles_from_csv(csv_filename):
    df = pd.read_csv(csv_filename)
    knee_angle_0 = df['Knee Angle'].min()
    hip_angle_0 = df['Hip Angle'].min()
    knee_angle_6 = df['Knee Angle'].max()
    hip_angle_6 = df['Hip Angle'].max()
    knee_angle_average = df['Knee Angle'].mean()
    hip_angle_average = df['Hip Angle'].mean()
    
    return (knee_angle_0, knee_angle_6, knee_angle_average, hip_angle_0, hip_angle_6, hip_angle_average)

def get_valid_float(prompt, min_val=0, max_val=300):
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Invalid input. Please enter a number.")
def get_valid_string(prompt, allowed_values=None):
    while True:
        value = input(prompt).strip()
        if allowed_values:
            if value in allowed_values:
                return value
            else:
                print(f"Please enter one of: {', '.join(allowed_values)}")
        elif value:  # Just check if not empty if no specific values required
            return value
        else:
            print("Input cannot be empty.")

def get_user_data():
    new_user = {
        'name': '',
        'height_cm': 0,
        'inseam_cm': 0,
        'arm_length_cm': 0,
        'torso_length_cm': 0,
        'bike_type': 'Road',
        'saddle_height_cm': 0,
        'handlebar_reach_cm': 0,
        'handlebar_width_cm': 0,
        'stack_height_cm': 0,
        'stack_angle': 0,
        'knee_angle_0': 0,
        'knee_angle_6': 0,
        'knee_angle_average': 0,
        'hip_angle_0': 0,
        'hip_angle_6': 0,
        'hip_angle_average': 0
    }

    print("Enter user profile information:")
    
    # Name input
    new_user['name'] = get_valid_string("Name: ")
    
    # Height measurements (assuming reasonable human ranges)
    new_user['height_cm'] = get_valid_float("Height (cm, 100-250): ", 100, 250)
    new_user['inseam_cm'] = get_valid_float("Inseam (cm, 60-100): ", 60, 100)
    new_user['arm_length_cm'] = get_valid_float("Arm length (cm, 40-100): ", 40, 100)
    new_user['torso_length_cm'] = get_valid_float("Torso length (cm, 40-100): ", 40, 100)
    
    # Bike type selection
    bike_types = ['Road', 'Mountain', 'Hybrid', 'TT']
    new_user['bike_type'] = get_valid_string("Bike type (Road/Mountain/Hybrid/TT): ", bike_types)
    
    # Bike fit measurements
    new_user['saddle_height_cm'] = get_valid_float("Saddle height (cm, 40-150): ", 40, 150)
    new_user['handlebar_reach_cm'] = get_valid_float("Handlebar reach (mm, 30-80): ", 30, 80)
    new_user['handlebar_width_cm'] = get_valid_float("Handlebar width (cm, 30-60): ", 30, 60)  
    new_user['stack_height_cm'] = get_valid_float("Stack height (mm, 40-80): ", 40, 80)
    new_user['stack_angle'] = get_valid_float("Stam angle (degrees, 0-90): ", 0, 90)
    
    return new_user


def collect_user_data_gui():
    def submit_data():
        new_user['name'] = name_entry.get() if name_entry.get() else 'Avrage Joe'
        new_user['height_cm'] = float(height_entry.get()) if height_entry.get() else 0
        new_user['bike_type'] = bike_type.get()
        new_user['inseam_cm'] = float(inseam_entry.get()) if inseam_entry.get() else 0
        new_user['arm_length_cm'] = float(arm_length_entry.get()) if arm_length_entry.get() else 0
        new_user['torso_length_cm'] = float(torso_length_entry.get()) if torso_length_entry.get() else 0
        new_user['saddle_height_cm'] = float(saddle_height_entry.get()) if saddle_height_entry.get() else 0
        new_user['handlebar_reach_cm'] = float(handlebar_reach_entry.get()) if handlebar_reach_entry.get() else 0
        new_user['handlebar_width_cm'] = float(handlebar_width_entry.get()) if handlebar_width_entry.get() else 0
        new_user['stack_height_cm'] = float(stack_height_entry.get()) if stack_height_entry.get() else 0
        new_user['stack_angle'] = float(stack_angle_entry.get()) if stack_angle_entry.get() else 0
        new_user['test_mode'] = test_mode_var.get()
        messagebox.showinfo("Data Collected", "User data successfully collected!")
        root.destroy()

    root = tk.Tk()
    root.title("Bike Fitting App")
    new_user = {}

    # Add test mode checkbox at the top
    test_mode_var = tk.BooleanVar(value=False)
    test_mode_checkbox = tk.Checkbutton(root, text="Test Mode (Use Video File)", variable=test_mode_var)
    test_mode_checkbox.grid(row=0, column=0, columnspan=2, pady=5)

    # Labels and entries
    tk.Label(root, text="Name").grid(row=1)
    tk.Label(root, text="Height (cm)").grid(row=2)
    tk.Label(root, text="Bike Type").grid(row=3)
    tk.Label(root, text="Inseam (cm)").grid(row=4)
    tk.Label(root, text="Arm Length (cm)").grid(row=5)
    tk.Label(root, text="Torso Length (cm)").grid(row=6)
    tk.Label(root, text="Saddle Height (cm)").grid(row=7)
    tk.Label(root, text="Handlebar Reach (cm)").grid(row=8)
    tk.Label(root, text="Handlebar Width (cm)").grid(row=9)
    tk.Label(root, text="Stack Height (cm)").grid(row=10)
    tk.Label(root, text="Stack Angle").grid(row=11)

    name_entry = tk.Entry(root)
    height_entry = tk.Entry(root)
    inseam_entry = tk.Entry(root)
    arm_length_entry = tk.Entry(root)
    torso_length_entry = tk.Entry(root)
    saddle_height_entry = tk.Entry(root)
    handlebar_reach_entry = tk.Entry(root)
    handlebar_width_entry = tk.Entry(root)
    stack_height_entry = tk.Entry(root)
    stack_angle_entry = tk.Entry(root)
    bike_type = tk.StringVar(value="Road")
    tk.OptionMenu(root, bike_type, "Road", "Mountain", "Hybrid", "TT").grid(row=3, column=1)

    name_entry.grid(row=1, column=1)
    height_entry.grid(row=2, column=1)
    inseam_entry.grid(row=4, column=1)
    arm_length_entry.grid(row=5, column=1)
    torso_length_entry.grid(row=6, column=1)
    saddle_height_entry.grid(row=7, column=1)
    handlebar_reach_entry.grid(row=8, column=1)
    handlebar_width_entry.grid(row=9, column=1)
    stack_height_entry.grid(row=10, column=1)
    stack_angle_entry.grid(row=11, column=1)

    tk.Button(root, text="Submit", command=submit_data).grid(row=12, column=1, pady=10)
    root.mainloop()

    return new_user

def process_video_file(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(video_path)

    knee_angles = []
    hip_angles = []

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )
            
            hip = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x,
                   results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y]
            knee = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x,
                    results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y]
            ankle = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x,
                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y]
            shoulder = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
            
            # Convert normalized coordinates to pixel coordinates
            h, w, _ = image.shape
            hip_px = (int(hip[0] * w), int(hip[1] * h))
            knee_px = (int(knee[0] * w), int(knee[1] * h))
            ankle_px = (int(ankle[0] * w), int(ankle[1] * h))
            shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))
            
            knee_angle = angle_calculator.calculate_angle(hip, knee, ankle)
            hip_angle = angle_calculator.calculate_angle(shoulder, hip, knee)
        
            knee_angles.append(round(knee_angle, 3))
            hip_angles.append(round(hip_angle, 3))
            
            # Display angles on the image
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            color = (0, 255, 0)  # Green in BGR
            thickness = 2
            
            # Display knee angle
            knee_text = f"Knee: {knee_angle:.1f}°"
            cv2.putText(image, knee_text, 
                       (knee_px[0] + 10, knee_px[1] + 10),
                       font, font_scale, color, thickness)
            
            # Display hip angle
            hip_text = f"Hip: {hip_angle:.1f}°"
            cv2.putText(image, hip_text,
                       (hip_px[0] + 10, hip_px[1] + 10),
                       font, font_scale, color, thickness)
            
            # Draw lines to make the angles more visible
            cv2.line(image, hip_px, knee_px, (0, 255, 0), 2)
            cv2.line(image, knee_px, ankle_px, (0, 255, 0), 2)
            cv2.line(image, shoulder_px, hip_px, (0, 255, 0), 2)

        cv2.imshow('Video Analysis', image)
        to_csv(knee_angles, hip_angles)

        if cv2.waitKey(5) & 0xFF == 27:
            break 

    cap.release()
    cv2.destroyAllWindows()
    return knee_angles, hip_angles

def write_out_user(user_data):
    print("User Bike Fit Profile:")
    print("-" * 20)
    for key, value in user_data.items():
        # Replace underscores with spaces and capitalize for readability
        label = key.replace('_', ' ').title()
        print(f"{label}: {value}")
    print("-" * 20)

    

def main():
    user_profile = collect_user_data_gui()
    
    if user_profile.get('test_mode', False):
        # Open file dialog to select video file
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        
        if video_path:
            knee_angles, hip_angles = process_video_file(video_path)
        else:
            print("No video file selected. Exiting...")
            return
    else:
        # Original camera capture code
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()
        cap = cv2.VideoCapture(1)

        knee_angles = []
        hip_angles = []

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )
                #get coordinates of landmarks
                hip = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x,
                       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y]
                knee = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x,
                        results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y]
                ankle = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x,
                         results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y]
                shoulder = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                           results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                
                # Convert normalized coordinates to pixel coordinates
                h, w, _ = image.shape
                hip_px = (int(hip[0] * w), int(hip[1] * h))
                knee_px = (int(knee[0] * w), int(knee[1] * h))
                ankle_px = (int(ankle[0] * w), int(ankle[1] * h))
                shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))
                
                #calculate angles
                knee_angle = angle_calculator.calculate_angle(hip, knee, ankle)
                hip_angle = angle_calculator.calculate_angle(shoulder, hip, knee)
            
                knee_angles.append(round(knee_angle, 3))
                hip_angles.append(round(hip_angle, 3))
                
                # Display angles on the image
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                color = (0, 255, 0)  # Green in BGR
                thickness = 2
                
                # Display knee angle
                knee_text = f"Knee: {knee_angle:.1f}°"
                cv2.putText(image, knee_text, 
                           (knee_px[0] + 10, knee_px[1] + 10),
                           font, font_scale, color, thickness)
                
                # Display hip angle
                hip_text = f"Hip: {hip_angle:.1f}°"
                cv2.putText(image, hip_text,
                           (hip_px[0] + 10, hip_px[1] + 10),
                           font, font_scale, color, thickness)
                
                # Draw lines to make the angles more visible
                cv2.line(image, hip_px, knee_px, (0, 255, 0), 2)
                cv2.line(image, knee_px, ankle_px, (0, 255, 0), 2)
                cv2.line(image, shoulder_px, hip_px, (0, 255, 0), 2)
                
                print(f'Knee: {knee_angle:.2f}, Hip: {hip_angle:.2f}')

            cv2.imshow('Test Pose', image)
            to_csv(knee_angles, hip_angles)
            print("Save successful")

            if cv2.waitKey(5) & 0xFF == 27:
                break 

        cap.release()
        cv2.destroyAllWindows()
    
    #handleing collected data
    bike_fit = User.BikeFitManager()
    
    knee_angle_0, knee_angle_6, knee_angle_average, hip_angle_0, hip_angle_6, hip_angle_average = angles_from_csv('test.csv')
    
    user_profile['knee_angle_0'] = knee_angle_0
    user_profile['knee_angle_6'] = knee_angle_6
    user_profile['knee_angle_average'] = knee_angle_average  
    user_profile['hip_angle_0'] = hip_angle_0
    user_profile['hip_angle_6'] = hip_angle_6
    user_profile['hip_angle_average'] = hip_angle_average  
    
    # Remove test_mode before adding to bike_fit data
    if 'test_mode' in user_profile:
        del user_profile['test_mode']
    
    bike_fit.add_user(user_profile)
    
    clear_terminal()
    write_out_user(user_profile)
    

if __name__ == "__main__":
    main()