import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better compatibility
import seaborn as sns
from scipy import signal
from scipy.interpolate import interp1d
import pandas as pd
from typing import List, Dict, Tuple, Optional
import math
import time
import os  # Added for directory operations
from datetime import datetime  # Added for timestamp generation

class PedalStrokeAnalyzer:
    def __init__(self):
        """Initialize the pedal stroke analyzer with plotting configuration"""
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
        
        # Analysis parameters
        self.min_stroke_duration = 0.3  # Minimum time for a complete stroke (seconds)
        self.max_stroke_duration = 3.0  # Maximum time for a complete stroke (seconds)
        self.smoothing_window = 5  # Window size for smoothing
        
        # Create plots directory if it doesn't exist (adjusted path for new structure)
        self.plots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
        
    def detect_pedal_strokes(self, knee_angles: List[float], timestamps: List[float]) -> List[Dict]:
        """
        Detect individual pedal strokes from continuous knee angle data.
        A stroke is defined as one complete cycle from minimum to maximum knee angle.
        """
        if len(knee_angles) < 10 or len(timestamps) != len(knee_angles):
            return []
        
        try:
            # Convert to numpy arrays for easier manipulation
            angles = np.array(knee_angles)
            times = np.array(timestamps)
            
            # Smooth the data to remove noise
            window_length = min(self.smoothing_window, len(angles))
            if window_length % 2 == 0:
                window_length += 1  # Must be odd
            
            if window_length >= 3:
                angles_smooth = signal.savgol_filter(angles, window_length, 2)
            else:
                angles_smooth = angles
            
            # Find local minima (bottom of pedal stroke) and maxima (top of pedal stroke)
            # Use prominence to filter out noise
            min_prominence = np.std(angles_smooth) * 0.3
            
            peaks, _ = signal.find_peaks(angles_smooth, prominence=min_prominence)
            valleys, _ = signal.find_peaks(-angles_smooth, prominence=min_prominence)
            
            if len(valleys) < 2:
                return []
            
            strokes = []
            
            # Create strokes from valley to valley (complete pedal cycles)
            for i in range(len(valleys) - 1):
                start_idx = valleys[i]
                end_idx = valleys[i + 1]
                
                # Validate stroke duration
                stroke_duration = times[end_idx] - times[start_idx]
                if self.min_stroke_duration <= stroke_duration <= self.max_stroke_duration:
                    
                    # Find the peak (maximum knee angle) within this stroke
                    peaks_in_stroke = peaks[(peaks > start_idx) & (peaks < end_idx)]
                    
                    if len(peaks_in_stroke) > 0:
                        peak_idx = peaks_in_stroke[0]
                        
                        stroke = {
                            'start_time': times[start_idx],
                            'peak_time': times[peak_idx],
                            'end_time': times[end_idx],
                            'duration': stroke_duration,
                            'min_angle': float(angles_smooth[start_idx]),
                            'max_angle': float(angles_smooth[peak_idx]),
                            'angle_range': float(angles_smooth[peak_idx] - angles_smooth[start_idx]),
                            'angles': angles_smooth[start_idx:end_idx+1].tolist(),
                            'timestamps': times[start_idx:end_idx+1].tolist(),
                            'cadence_rpm': 60.0 / stroke_duration  # RPM calculation
                        }
                        strokes.append(stroke)
            
            return strokes
            
        except Exception as e:
            print(f"Error in pedal stroke detection: {e}")
            return []
    
    def analyze_fluidity(self, strokes: List[Dict]) -> Dict:
        """
        Analyze the fluidity and smoothness of pedal strokes.
        Returns metrics for stroke quality assessment.
        """
        if not strokes:
            return {'error': 'No strokes available for analysis'}
        
        fluidity_metrics = {
            'smoothness_scores': [],
            'consistency_scores': [],
            'angular_velocity_variations': [],
            'power_distribution_scores': []
        }
        
        for stroke in strokes:
            angles = np.array(stroke['angles'])
            times = np.array(stroke['timestamps'])
            
            # Calculate smoothness (based on angular acceleration changes)
            if len(angles) >= 3:
                # Calculate angular velocity (rate of angle change)
                angular_velocity = np.gradient(angles, times)
                
                # Calculate angular acceleration
                angular_acceleration = np.gradient(angular_velocity, times)
                
                # Smoothness score: lower variation in acceleration = smoother
                smoothness = 1.0 / (1.0 + np.std(angular_acceleration))
                fluidity_metrics['smoothness_scores'].append(smoothness)
                
                # Angular velocity variation
                vel_variation = np.std(angular_velocity) / (np.mean(np.abs(angular_velocity)) + 1e-6)
                fluidity_metrics['angular_velocity_variations'].append(vel_variation)
                
                # Power distribution analysis (estimated from angle changes)
                normalized_phase = np.linspace(0, 1, len(angles))
                power_stroke_phase = (normalized_phase >= 0.0) & (normalized_phase <= 0.5)
                recovery_phase = normalized_phase > 0.5
                
                power_stroke_work = np.sum(np.diff(angles[power_stroke_phase]) ** 2) if np.sum(power_stroke_phase) > 1 else 0
                recovery_work = np.sum(np.diff(angles[recovery_phase]) ** 2) if np.sum(recovery_phase) > 1 else 0
                
                total_work = power_stroke_work + recovery_work + 1e-6
                power_distribution = power_stroke_work / total_work
                fluidity_metrics['power_distribution_scores'].append(power_distribution)
        
        # Calculate consistency between strokes
        if len(strokes) >= 2:
            durations = [s['duration'] for s in strokes]
            angle_ranges = [s['angle_range'] for s in strokes]
            cadences = [s['cadence_rpm'] for s in strokes]
            
            duration_consistency = 1.0 / (1.0 + np.std(durations) / np.mean(durations))
            range_consistency = 1.0 / (1.0 + np.std(angle_ranges) / np.mean(angle_ranges))
            cadence_consistency = 1.0 / (1.0 + np.std(cadences) / np.mean(cadences))
            
            overall_consistency = np.mean([duration_consistency, range_consistency, cadence_consistency])
            fluidity_metrics['consistency_scores'].append(overall_consistency)
        
        # Aggregate results
        results = {
            'average_smoothness': np.mean(fluidity_metrics['smoothness_scores']) if fluidity_metrics['smoothness_scores'] else 0,
            'consistency_score': np.mean(fluidity_metrics['consistency_scores']) if fluidity_metrics['consistency_scores'] else 0,
            'velocity_stability': 1.0 / (1.0 + np.mean(fluidity_metrics['angular_velocity_variations'])) if fluidity_metrics['angular_velocity_variations'] else 0,
            'power_distribution': np.mean(fluidity_metrics['power_distribution_scores']) if fluidity_metrics['power_distribution_scores'] else 0,
            'overall_fluidity_score': 0
        }
        
        # Calculate overall fluidity score (weighted average)
        weights = [0.3, 0.25, 0.25, 0.2]  # smoothness, consistency, velocity, power
        scores = [results['average_smoothness'], results['consistency_score'], 
                 results['velocity_stability'], results['power_distribution']]
        
        results['overall_fluidity_score'] = np.average(scores, weights=weights)
        
        return results
    
    def calculate_pedaling_dynamics(self, strokes: List[Dict]) -> Dict:
        """
        Calculate comprehensive pedaling dynamics including cadence analysis,
        power distribution, and efficiency metrics.
        """
        if not strokes:
            return {'error': 'No strokes available for analysis'}
        
        dynamics = {
            'cadence_rpm': [s['cadence_rpm'] for s in strokes],
            'stroke_durations': [s['duration'] for s in strokes],
            'angle_ranges': [s['angle_range'] for s in strokes],
            'min_angles': [s['min_angle'] for s in strokes],
            'max_angles': [s['max_angle'] for s in strokes]
        }
        
        # Calculate statistics
        results = {
            'average_cadence': np.mean(dynamics['cadence_rpm']),
            'cadence_variability': np.std(dynamics['cadence_rpm']),
            'average_stroke_duration': np.mean(dynamics['stroke_durations']),
            'average_angle_range': np.mean(dynamics['angle_ranges']),
            'range_consistency': 1.0 / (1.0 + np.std(dynamics['angle_ranges']) / np.mean(dynamics['angle_ranges'])),
            'min_knee_angle_avg': np.mean(dynamics['min_angles']),
            'max_knee_angle_avg': np.mean(dynamics['max_angles']),
            'total_strokes': len(strokes),
            'stroke_rate_per_minute': len(strokes) * 60.0 / (strokes[-1]['end_time'] - strokes[0]['start_time']) if len(strokes) > 1 else 0
        }
        
        # Add efficiency estimation
        ideal_cadence_range = (80, 100)  # Typical efficient cadence range
        cadence_efficiency = 1.0 - min(abs(results['average_cadence'] - ideal_cadence_range[0]), 
                                      abs(results['average_cadence'] - ideal_cadence_range[1])) / ideal_cadence_range[1]
        results['cadence_efficiency'] = max(0, cadence_efficiency)
        
        return results
    
    def create_dynamic_plots(self, strokes: List[Dict], fluidity_analysis: Dict, 
                           dynamics_analysis: Dict, user_data: Dict = None) -> str:
        """
        Create comprehensive dynamic plots showing pedaling analysis.
        This creates multiple subplots in one figure and saves it to the plots folder.
        Returns the path to the saved plot file.
        """
        if not strokes:
            print("No stroke data available for plotting")
            return None
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        user_name = user_data.get("name", "User") if user_data else "User"
        fig.suptitle(f'Pedal Stroke Analysis - {user_name}', 
                    fontsize=16, fontweight='bold')
        
        # Plot 1: Stroke overlay (top left)
        ax1 = plt.subplot(2, 3, 1)
        self._plot_stroke_overlay(ax1, strokes)
        
        # Plot 2: Cadence analysis (top middle)
        ax2 = plt.subplot(2, 3, 2)
        self._plot_cadence_analysis(ax2, strokes, dynamics_analysis)
        
        # Plot 3: Fluidity metrics (top right)
        ax3 = plt.subplot(2, 3, 3)
        self._plot_fluidity_metrics(ax3, fluidity_analysis)
        
        # Plot 4: Power distribution (bottom left)
        ax4 = plt.subplot(2, 3, 4)
        self._plot_power_distribution(ax4, strokes)
        
        # Plot 5: Angle progression (bottom middle)
        ax5 = plt.subplot(2, 3, 5)
        self._plot_angle_progression(ax5, strokes)
        
        # Plot 6: Summary dashboard (bottom right)
        ax6 = plt.subplot(2, 3, 6)
        self._plot_summary_dashboard(ax6, fluidity_analysis, dynamics_analysis)
        
        plt.tight_layout()
        
        # Generate filename with timestamp and user name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_user_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_user_name = clean_user_name.replace(' ', '_')
        filename = f"pedal_analysis_{clean_user_name}_{timestamp}.png"
        file_path = os.path.join(self.plots_dir, filename)
        
        # Save the figure
        try:
            plt.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"✅ Plot saved successfully: {file_path}")
        except Exception as e:
            print(f"❌ Error saving plot: {e}")
            file_path = None
        
        # Display the plot
        plt.show(block=False)  # Non-blocking show
        
        return file_path
    
    def _plot_stroke_overlay(self, ax, strokes: List[Dict]):
        """Plot overlaid individual strokes"""
        ax.set_title('Individual Pedal Strokes', fontweight='bold', fontsize=12)
        
        colors = plt.cm.viridis(np.linspace(0, 1, min(len(strokes), 10)))
        
        for i, stroke in enumerate(strokes[:10]):  # Show max 10 strokes
            normalized_phase = np.linspace(0, 100, len(stroke['angles']))
            ax.plot(normalized_phase, stroke['angles'], 
                   color=colors[i], alpha=0.7, linewidth=2, 
                   label=f'Stroke {i+1}' if i < 5 else '')
        
        ax.set_xlabel('Pedal Cycle Phase (%)')
        ax.set_ylabel('Knee Angle (degrees)')
        ax.grid(True, alpha=0.3)
        if len(strokes) <= 5:
            ax.legend()
    
    def _plot_cadence_analysis(self, ax, strokes: List[Dict], dynamics: Dict):
        """Plot cadence over time"""
        ax.set_title('Cadence Analysis', fontweight='bold', fontsize=12)
        
        cadences = [s['cadence_rpm'] for s in strokes]
        stroke_numbers = range(1, len(cadences) + 1)
        
        ax.plot(stroke_numbers, cadences, 'bo-', linewidth=2, markersize=6)
        ax.axhline(y=dynamics['average_cadence'], color='r', linestyle='--', 
                  label=f'Avg: {dynamics["average_cadence"]:.1f} RPM')
        
        # Add target zone
        ax.axhspan(80, 100, alpha=0.2, color='green', label='Efficient Zone')
        
        ax.set_xlabel('Stroke Number')
        ax.set_ylabel('Cadence (RPM)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_fluidity_metrics(self, ax, fluidity: Dict):
        """Plot fluidity metrics as a radar chart"""
        ax.set_title('Fluidity Metrics', fontweight='bold', fontsize=12)
        
        metrics = ['Smoothness', 'Consistency', 'Velocity\nStability', 'Power\nDistribution']
        values = [
            fluidity.get('average_smoothness', 0),
            fluidity.get('consistency_score', 0),
            fluidity.get('velocity_stability', 0),
            fluidity.get('power_distribution', 0)
        ]
        
        # Convert to percentages and ensure values are in [0, 1] range
        values = [max(0, min(1, v)) * 100 for v in values]
        
        bars = ax.bar(metrics, values, color=['skyblue', 'lightgreen', 'orange', 'lightcoral'])
        
        # Color bars based on performance
        for bar, val in zip(bars, values):
            if val >= 80:
                bar.set_color('green')
                bar.set_alpha(0.7)
            elif val >= 60:
                bar.set_color('orange')
                bar.set_alpha(0.7)
            else:
                bar.set_color('red')
                bar.set_alpha(0.7)
        
        ax.set_ylabel('Score (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=10)
    
    def _plot_power_distribution(self, ax, strokes: List[Dict]):
        """Plot estimated power distribution through stroke cycle"""
        ax.set_title('Power Distribution', fontweight='bold', fontsize=12)
        
        if not strokes:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            return
        
        # Average stroke for power analysis
        avg_stroke = self._calculate_average_stroke(strokes)
        if avg_stroke is None:
            return
        
        phases = np.linspace(0, 360, len(avg_stroke))
        
        # Estimate power as derivative of angle (simplified model)
        power_estimate = np.abs(np.gradient(avg_stroke))
        power_normalized = (power_estimate / np.max(power_estimate)) * 100
        
        ax.plot(phases, power_normalized, 'r-', linewidth=3, label='Power Estimate')
        ax.fill_between(phases, power_normalized, alpha=0.3, color='red')
        
        # Mark power and recovery phases
        ax.axvspan(0, 180, alpha=0.1, color='green', label='Power Phase')
        ax.axvspan(180, 360, alpha=0.1, color='blue', label='Recovery Phase')
        
        ax.set_xlabel('Crank Angle (degrees)')
        ax.set_ylabel('Relative Power (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_angle_progression(self, ax, strokes: List[Dict]):
        """Plot knee angle progression over time"""
        ax.set_title('Knee Angle Progression', fontweight='bold', fontsize=12)
        
        all_times = []
        all_angles = []
        
        for stroke in strokes:
            all_times.extend(stroke['timestamps'])
            all_angles.extend(stroke['angles'])
        
        if all_times:
            # Convert to relative time (seconds from start)
            start_time = min(all_times)
            relative_times = [(t - start_time) for t in all_times]
            
            ax.plot(relative_times, all_angles, 'b-', linewidth=1, alpha=0.8)
            
            # Mark stroke boundaries
            for stroke in strokes:
                stroke_start = stroke['start_time'] - start_time
                ax.axvline(x=stroke_start, color='red', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Knee Angle (degrees)')
        ax.grid(True, alpha=0.3)
    
    def _plot_summary_dashboard(self, ax, fluidity: Dict, dynamics: Dict):
        """Create a summary dashboard with key metrics"""
        ax.set_title('Summary Dashboard', fontweight='bold', fontsize=12)
        ax.axis('off')  # Turn off axes for text display
        
        # Prepare summary text
        summary_text = f"""
PEDALING PERFORMANCE SUMMARY

Cadence: {dynamics.get('average_cadence', 0):.1f} ± {dynamics.get('cadence_variability', 0):.1f} RPM
Total Strokes: {dynamics.get('total_strokes', 0)}
Avg Duration: {dynamics.get('average_stroke_duration', 0):.2f}s

FLUIDITY SCORES:
Overall: {fluidity.get('overall_fluidity_score', 0)*100:.1f}%
Smoothness: {fluidity.get('average_smoothness', 0)*100:.1f}%
Consistency: {fluidity.get('consistency_score', 0)*100:.1f}%

EFFICIENCY:
Cadence Efficiency: {dynamics.get('cadence_efficiency', 0)*100:.1f}%
Range Consistency: {dynamics.get('range_consistency', 0)*100:.1f}%

RECOMMENDATIONS:
"""
        
        # Add recommendations based on analysis
        recommendations = self._generate_recommendations(fluidity, dynamics)
        summary_text += "\n".join([f"• {rec}" for rec in recommendations])
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
    
    def _calculate_average_stroke(self, strokes: List[Dict]) -> Optional[List[float]]:
        """Calculate average stroke pattern from multiple strokes"""
        if not strokes:
            return None
        
        # Normalize all strokes to same length
        target_length = 50
        normalized_strokes = []
        
        for stroke in strokes:
            angles = stroke['angles']
            if len(angles) >= 5:  # Minimum valid stroke
                # Interpolate to target length
                old_indices = np.linspace(0, 1, len(angles))
                new_indices = np.linspace(0, 1, target_length)
                try:
                    interpolator = interp1d(old_indices, angles, kind='linear')
                    normalized_stroke = interpolator(new_indices)
                    normalized_strokes.append(normalized_stroke)
                except:
                    continue
        
        if normalized_strokes:
            return np.mean(normalized_strokes, axis=0).tolist()
        return None
    
    def _generate_recommendations(self, fluidity: Dict, dynamics: Dict) -> List[str]:
        """Generate personalized recommendations based on analysis"""
        recommendations = []
        
        # Cadence recommendations
        avg_cadence = dynamics.get('average_cadence', 0)
        if avg_cadence < 70:
            recommendations.append("Increase cadence - aim for 80-100 RPM")
        elif avg_cadence > 110:
            recommendations.append("Decrease cadence for better efficiency")
        
        # Consistency recommendations
        consistency = fluidity.get('consistency_score', 0)
        if consistency < 0.7:
            recommendations.append("Focus on maintaining consistent stroke rhythm")
        
        # Smoothness recommendations
        smoothness = fluidity.get('average_smoothness', 0)
        if smoothness < 0.6:
            recommendations.append("Work on smoother pedal transitions")
        
        # Power distribution recommendations
        power_dist = fluidity.get('power_distribution', 0)
        if power_dist < 0.6:
            recommendations.append("Focus more power on downstroke phase")
        
        if not recommendations:
            recommendations.append("Excellent pedaling technique!")
        
        return recommendations 