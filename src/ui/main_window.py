import sys
import os
import time
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog,
                             QLineEdit, QFormLayout, QGroupBox, QProgressBar, QDialog, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.analyzers.video_processor import BikeFitProcessor
from src.data import BikeFitManager
from src.analyzers.pedal_stroke_analyzer import PedalStrokeAnalyzer
from src.analyzers.pedal_stroke_analyzer import PedalStrokeAnalyzer
from src.utils import calculate_angle_stats, write_out_user

# ==========================================
# UI STYLE CONFIGURATION
# Modify these values to customize the application look (when not using qt_material)
# ==========================================
STYLE_CONFIG = {
    "main_bg": "#2b2b2b",
    "main_text": "#ffffff",
    "group_border_color": "#555555",
    "group_border_width": "2px",          # Increased visibility
    "group_border_radius": "6px",
    "input_bg": "#3b3b3b",
    "input_border": "#555555",
    "btn_primary": "#0d6efd",
    "btn_hover": "#0b5ed7",
    "btn_radius": "6px",
    "video_label_bg": "#000000",
    "video_label_text": "#666666"
}

class AnalysisResultWindow(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Results")
        self.resize(1000, 800)
        
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        
        # Scale if too large, but keep aspect ratio
        if not pixmap.isNull():
             if pixmap.width() > 1600:
                pixmap = pixmap.scaledToWidth(1600, Qt.SmoothTransformation)
             image_label.setPixmap(pixmap)
             image_label.setAlignment(Qt.AlignCenter)
        else:
             image_label.setText("Error loading result image.")
        
        scroll.setWidget(image_label)
        layout.addWidget(scroll)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class VideoThread(QThread):
    change_pixmap_signal = Signal(QImage)
    update_data_signal = Signal(dict)
    finished_signal = Signal()

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.source = 0  # Default to camera
        self.processor = None
        self.recording_data = False
        self.collected_knee_angles = []
        self.collected_hip_angles = []
        self.collected_timestamps = []
        self.start_time = 0

    def set_source(self, source):
        self.source = source

    def start_recording(self):
        self.collected_knee_angles = []
        self.collected_hip_angles = []
        self.collected_timestamps = []
        self.start_time = time.time()
        self.recording_data = True

    def stop_recording(self):
        self.recording_data = False
        return (self.collected_knee_angles, self.collected_hip_angles, self.collected_timestamps)

    def run(self):
        self._run_flag = True
        cap = cv2.VideoCapture(self.source)
        
        if not cap.isOpened():
            print(f"Error opening source: {self.source}")
            return

        self.processor = BikeFitProcessor()
        
        is_video_file = isinstance(self.source, str)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or not is_video_file:
            fps = 30 # Default assumption
            
        frame_delay = int(1000 / fps) if is_video_file else 1

        while self._run_flag and cap.isOpened():
            ret, cv_img = cap.read()
            if not ret:
                break
            
            # Timestamp calculation
            if is_video_file:
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                # Artificial delay for video files to match playback speed loosely 
                # (though processing might be slower, this prevents super-fast forward on simple frames)
                self.msleep(max(1, frame_delay - 20)) # simple throttle
            else:
                current_time = time.time() - self.start_time

            processed_img, data = self.processor.process_frame(cv_img)
            
            if data and self.recording_data:
                self.collected_knee_angles.append(data['knee_angle'])
                self.collected_hip_angles.append(data['hip_angle'])
                self.collected_timestamps.append(current_time)
                self.update_data_signal.emit(data)

            qt_img = self._convert_cv_qt(processed_img)
            self.change_pixmap_signal.emit(qt_img)
        
        cap.release()
        self.processor.close()
        self.finished_signal.emit()

    def _convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return convert_to_Qt_format

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BikeFit Pro - AI Biomechanics Analyzer")
        self.resize(1200, 800)
        
        # Data
        self.user_data = {}
        self.thread = None

        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self._setup_video_panel()
        self._setup_sidebar()
        
        # Apply Dark Theme manually if qt_material is missing, or simple styles
        self._apply_styles()

    def _setup_video_panel(self):
        self.video_container = QGroupBox("Live Analysis Feed")
        video_layout = QVBoxLayout(self.video_container)
        
        self.video_label = QLabel("Camera Offline")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet(f"background-color: {STYLE_CONFIG['video_label_bg']}; color: {STYLE_CONFIG['video_label_text']}; font-size: 20px;")
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setMinimumSize(640, 480)
        
        video_layout.addWidget(self.video_label)
        self.main_layout.addWidget(self.video_container, stretch=3)

    def _setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(350)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        # 1. User Info
        info_group = QGroupBox("Rider Profile")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.height_input = QLineEdit()
        self.bike_type_input = QLineEdit()
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Height (cm):", self.height_input)
        form_layout.addRow("Bike Type:", self.bike_type_input)
        
        info_group.setLayout(form_layout)
        sidebar_layout.addWidget(info_group)
        
        # 2. Controls
        control_group = QGroupBox("Controls")
        ctrl_layout = QVBoxLayout()
        
        self.btn_camera = QPushButton("Start Camera")
        self.btn_camera.clicked.connect(self.start_camera)
        
        self.btn_video = QPushButton("Load Video File")
        self.btn_video.clicked.connect(self.load_video)
        
        self.btn_record = QPushButton("Start Recording / Analysis")
        self.btn_record.setCheckable(True)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_record.setEnabled(False)
        
        ctrl_layout.addWidget(self.btn_camera)
        ctrl_layout.addWidget(self.btn_video)
        ctrl_layout.addWidget(self.btn_record)
        
        control_group.setLayout(ctrl_layout)
        sidebar_layout.addWidget(control_group)
        
        # 3. Live Stats
        stats_group = QGroupBox("Live Biometrics")
        stats_layout = QVBoxLayout()
        
        self.lbl_knee = QLabel("Knee Angle: --°")
        self.lbl_knee.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_hip = QLabel("Hip Angle: --°")
        self.lbl_hip.setFont(QFont("Arial", 16, QFont.Bold))
        
        stats_layout.addWidget(self.lbl_knee)
        stats_layout.addWidget(self.lbl_hip)
        stats_group.setLayout(stats_layout)
        sidebar_layout.addWidget(stats_group)
        
        # 4. Status / Results
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        sidebar_layout.addWidget(self.status_label)
        
        sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar, stretch=1)

    def _apply_styles(self):
        # Basic Dark Theme Stylesheet (Fallback or Custom)
        # Uses values from STYLE_CONFIG dictionary defined at the top of the file
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {STYLE_CONFIG['main_bg']}; color: {STYLE_CONFIG['main_text']}; }}
            QGroupBox {{ 
                font-weight: bold; 
                border: {STYLE_CONFIG['group_border_width']} solid {STYLE_CONFIG['group_border_color']}; 
                border-radius: {STYLE_CONFIG['group_border_radius']};
                margin-top: 10px; padding-top: 12px; color: #ddd;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
            QLabel {{ color: {STYLE_CONFIG['main_text']}; }}
            QLineEdit {{ 
                background-color: {STYLE_CONFIG['input_bg']}; color: #fff; 
                border: 1px solid {STYLE_CONFIG['input_border']}; 
                padding: 5px; border-radius: 4px;
            }}
            QPushButton {{
                background-color: {STYLE_CONFIG['btn_primary']}; color: white; border: none;
                padding: 8px 16px; border-radius: {STYLE_CONFIG['btn_radius']}; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {STYLE_CONFIG['btn_hover']}; }}
            QPushButton:disabled {{ background-color: #555; color: #888; }}
            QPushButton:checked {{ background-color: #dc3545; }}
        """)

    @Slot(QImage)
    def update_image(self, qt_img):
        """Updates the image_label with a new opencv image"""
        self.video_label.setPixmap(QPixmap.fromImage(qt_img).scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))

    @Slot(dict)
    def update_data(self, data):
        self.lbl_knee.setText(f"Knee Angle: {data['knee_angle']}°")
        self.lbl_hip.setText(f"Hip Angle: {data['hip_angle']}°")

    def start_camera(self):
        self._start_thread(0)

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_name:
            self._start_thread(file_name)

    def _start_thread(self, source):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        
        self.thread = VideoThread()
        self.thread.set_source(source)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_data_signal.connect(self.update_data)
        self.thread.finished_signal.connect(self.on_processing_finished)
        self.thread.start()
        
        self.btn_record.setEnabled(True)
        self.status_label.setText(f"Source loaded: {source}")

    def toggle_recording(self):
        if not self.thread or not self.thread.isRunning():
            return
            
        if self.btn_record.isChecked():
            # Start Recording
            self.btn_record.setText("Stop & Analyze")
            self.thread.start_recording()
            self.status_label.setText("Recording data... Perform pedal strokes.")
        else:
            # Stop & Analyze
            self.btn_record.setText("Start Recording / Analysis")
            self.btn_record.setEnabled(False) # Prevent restart while processing
            
            knee, hip, stamps = self.thread.stop_recording()
            self.process_results(knee, hip, stamps)

    def on_processing_finished(self):
        self.status_label.setText("Video source finished.")
        self.btn_record.setChecked(False)
        self.btn_record.setText("Start Recording / Analysis")

    def process_results(self, knee_angles, hip_angles, timestamps):
        self.status_label.setText("Analyzing collected data...")
        
        if not knee_angles or len(knee_angles) < 10:
            self.status_label.setText("Insufficient data collected.")
            self.btn_record.setEnabled(True)
            return

        # 1. Save User Data
        user_profile = {
            "name": self.name_input.text() or "Unknown",
            "age": self.age_input.text(),
            "height": self.height_input.text(),
            "bike_type": self.bike_type_input.text()
        }
        
        # Calculate stats
        k_min, k_max, k_avg, h_min, h_max, h_avg = calculate_angle_stats(knee_angles, hip_angles)
        user_profile.update({
            'knee_angle_0': k_min, 'knee_angle_6': k_max, 'knee_angle_average': k_avg,
            'hip_angle_0': h_min, 'hip_angle_6': h_max, 'hip_angle_average': h_avg
        })
        
        # Write to CSV
        BikeFitManager().add_user(user_profile)
        write_out_user(user_profile)
        
        # 2. Advanced Analysis & Plots
        analyzer = PedalStrokeAnalyzer()
        strokes = analyzer.detect_pedal_strokes(knee_angles, timestamps)
        
        if strokes:
            fluidity = analyzer.analyze_fluidity(strokes)
            dynamics = analyzer.calculate_pedaling_dynamics(strokes)
            
            plot_path = analyzer.create_dynamic_plots(strokes, fluidity, dynamics, user_profile)
            
            summary = (f"Analysis Complete!\n"
                       f"Cadence: {dynamics.get('average_cadence', 0):.1f} RPM\n"
                       f"Fluidity: {fluidity.get('overall_fluidity_score', 0)*100:.1f}%")
            
            if plot_path:
                summary += f"\nPlot saved to: {os.path.basename(plot_path)}"
                # Show results window
                result_window = AnalysisResultWindow(plot_path, self)
                result_window.exec()
            
            self.status_label.setText(summary)
        else:
            self.status_label.setText("Analysis Complete. No clear pedal strokes detected.")
        
        self.btn_record.setEnabled(True)

def run_gui():
    app = QApplication(sys.argv)
    
    # Try to apply qt_material if installed
    try:
        from qt_material import apply_stylesheet
        apply_stylesheet(app, theme='dark_teal.xml')
    except ImportError:
        print("qt_material not found, using internal dark theme.")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
