#!/usr/bin/env python3
"""
BikeFit - Advanced Bicycle Fitting Application with Pedal Stroke Analysis

A comprehensive bike fitting application that uses computer vision to analyze
cycling posture and pedal stroke dynamics for optimal bike setup.
"""

import mediapipe as mp
from tkinter import filedialog

# Import from our restructured modules
from src.analyzers import PedalStrokeAnalyzer
from src.analyzers.video_processor import process_media
from src.data import BikeFitManager
from src.ui.gui import collect_user_data_gui
from src.utils import (
    clear_terminal, 
    calculate_angle_stats,
    write_out_user
)

def main():
    """Main application entry point"""
    print(" BikeFit - Advanced Bicycle Fitting Application")
    print("=" * 60)
    
    user_profile = collect_user_data_gui()
    
    if not user_profile:
        print("User cancelled data entry. Exiting...")
        return

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    source = 0
    if user_profile.get('test_mode', False):
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        if video_path:
            print(f"🎥 Processing video file: {video_path}")
            source = video_path
        else:
            print("No video file selected. Exiting...")
            return
    else:
        print("📷 Starting live camera analysis... Press ESC to stop.")
        source = 0 

    knee_angles, hip_angles, timestamps = process_media(source, pose)
    
    if not (knee_angles and hip_angles and timestamps):
        print("❌ No data was collected from the video source.")
        return

    # ======= BIKE FIT DATA PROCESSING =======
    print("\n" + "="*50)
    print("PROCESSING BIKE FIT DATA")
    print("="*50)
    
    bike_fit = BikeFitManager()
    
    knee_angle_min, knee_angle_max, knee_angle_avg, hip_angle_min, hip_angle_max, hip_angle_avg = calculate_angle_stats(knee_angles, hip_angles)
    
    user_profile['knee_angle_0'] = knee_angle_min
    user_profile['knee_angle_6'] = knee_angle_max
    user_profile['knee_angle_average'] = knee_angle_avg
    user_profile['hip_angle_0'] = hip_angle_min
    user_profile['hip_angle_6'] = hip_angle_max
    user_profile['hip_angle_average'] = hip_angle_avg  
    
    if 'test_mode' in user_profile:
        del user_profile['test_mode']
    
    bike_fit.add_user(user_profile)
    
    clear_terminal()
    write_out_user(user_profile)
    
    # ======= PEDAL STROKE ANALYSIS SECTION =======
    print("\n" + "="*50)
    print("🔬 STARTING ADVANCED PEDAL STROKE ANALYSIS")
    print("="*50)
    
    stroke_analyzer = PedalStrokeAnalyzer()
    
    if timestamps and len(knee_angles) > 10:
        print(f"📊 Analyzing {len(knee_angles)} data points over {timestamps[-1]:.1f} seconds...")
        
        strokes = stroke_analyzer.detect_pedal_strokes(knee_angles, timestamps)
        
        if strokes:
            print(f"✅ Found {len(strokes)} complete pedal strokes!")
            
            fluidity_analysis = stroke_analyzer.analyze_fluidity(strokes)
            dynamics_analysis = stroke_analyzer.calculate_pedaling_dynamics(strokes)
            
            # Display results and plots
            print_analysis_results(dynamics_analysis, fluidity_analysis)
            
            recommendations = stroke_analyzer._generate_recommendations(fluidity_analysis, dynamics_analysis)
            print_recommendations(recommendations)

            try:
                saved_plot_path = stroke_analyzer.create_dynamic_plots(strokes, fluidity_analysis, dynamics_analysis, user_profile)
                if saved_plot_path:
                    print(f"📊 Analysis plots saved to: {saved_plot_path}")
                else:
                    print("⚠️  Plot created but not saved")
                
                input("Press Enter after viewing the plots to exit...")
                
            except Exception as e:
                print(f"❌ Error creating plots: {e}")
                
        else:
            print("❌ No complete pedal strokes detected.")
            
    else:
        print("❌ Insufficient data for pedal stroke analysis.")
    
    print("\n" + "="*50)
    print("🎉 BIKEFIT ANALYSIS COMPLETE")
    print("="*50)

def print_analysis_results(dynamics, fluidity):
    """Prints the formatted analysis results to the console."""
    print("\n" + "-"*40)
    print("📋 PEDAL STROKE ANALYSIS RESULTS")
    print("-"*40)
    print(f"🔢 Total Strokes Detected: {dynamics.get('total_strokes', 0)}")
    print(f"⚡ Average Cadence: {dynamics.get('average_cadence', 0):.1f} ± {dynamics.get('cadence_variability', 0):.1f} RPM")
    print(f"\n🎯 FLUIDITY SCORES:")
    print(f"Overall: {fluidity.get('overall_fluidity_score', 0)*100:.1f}%")
    print(f"Smoothness: {fluidity.get('average_smoothness', 0)*100:.1f}%")

def print_recommendations(recommendations):
    """Prints personalized recommendations."""
    print(f"\n💡 PERSONALIZED RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"• {rec}")

if __name__ == "__main__":
    main()