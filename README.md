# 🚴‍♂️ BikeFit - Advanced Bicycle Fitting Application

A comprehensive bicycle fitting application that uses computer vision and advanced analytics to analyze cycling posture and pedal stroke dynamics for optimal bike setup.

## 🌟 Features

### Core Bike Fitting
- **Real-time Pose Analysis**: Uses MediaPipe for accurate body position tracking
- **Angle Measurements**: Precise knee and hip angle calculations
- **User Profile Management**: Complete cyclist profile with body measurements and bike setup
- **Data Persistence**: CSV-based storage for historical analysis

### Advanced Pedal Stroke Analysis
- **Stroke Detection**: Automatic identification of individual pedal cycles
- **Fluidity Analysis**: Measures smoothness and consistency of pedaling technique
- **Cadence Tracking**: Real-time RPM calculation and rhythm analysis
- **Power Distribution**: Estimated force application throughout the stroke cycle
- **Dynamic Visualization**: 6 comprehensive analysis charts
- **Personalized Recommendations**: AI-generated coaching suggestions

### Technical Capabilities
- **Video Analysis**: Process pre-recorded cycling videos
- **Live Camera**: Real-time analysis during cycling sessions
- **High-Quality Plots**: Professional-grade visualization with automatic saving
- **Modular Architecture**: Clean, organized codebase for easy maintenance

## 📁 Project Structure

```
BikeFit/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/                        # Source code
│   ├── __init__.py
│   ├── analyzers/              # Analysis modules
│   │   ├── __init__.py
│   │   ├── angle_calculator.py # Angle calculation functions
│   │   └── pedal_stroke_analyzer.py # Advanced stroke analysis
│   ├── data/                   # Data management
│   │   ├── __init__.py
│   │   └── user_manager.py     # User profile management
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── helpers.py          # Common helper functions
├── data/                       # Data files
│   ├── bike_fit_data.csv      # User profile database
│   ├── test.csv               # Latest measurement data
│   └── *.csv                  # Additional measurement files
├── plots/                      # Generated analysis plots
│   └── pedal_analysis_*.png   # Saved analysis charts
├── docs/                       # Documentation
│   └── PEDAL_STROKE_ANALYSIS_README.md
└── videos/                     # Test videos (optional)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd BikeFit

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Choose Analysis Mode

**Live Camera Mode:**
- Position camera to capture side view of cyclist
- Start pedaling continuously for 15+ seconds
- Press ESC to stop and analyze

**Video Analysis Mode:**
- Check "Test Mode (Use Video File)" in GUI
- Select a cycling video (MP4, AVI, MOV)
- Ensure clear side view of cyclist

## 📊 Understanding Your Results

### Fluidity Scores (0-100%)
- **80-100%**: Excellent (Professional-level technique)
- **60-79%**: Good (Solid recreational cyclist)
- **40-59%**: Fair (Room for improvement)
- **0-39%**: Poor (Focus on basic technique)

### Analysis Charts
1. **Individual Pedal Strokes**: Overlay of stroke patterns
2. **Cadence Analysis**: RPM tracking with efficiency zones
3. **Fluidity Metrics**: Performance scores breakdown
4. **Power Distribution**: Force application through stroke cycle
5. **Angle Progression**: Knee angle changes over time
6. **Summary Dashboard**: Key metrics and recommendations

## 🔧 Requirements

### System Requirements
- Python 3.7+
- Webcam or video files for analysis
- At least 4GB RAM recommended

### Python Dependencies
- opencv-python >= 4.5.0
- mediapipe >= 0.8.0
- numpy >= 1.20.0
- pandas >= 1.3.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- scipy >= 1.7.0
- tkinter (usually included with Python)

## 📈 Best Practices for Analysis

### Camera Setup
- **Position**: Side view capturing full leg movement
- **Distance**: 2-3 meters from cyclist
- **Height**: Camera at hip level
- **Lighting**: Good, even lighting without shadows

### Recording Guidelines
- **Duration**: Minimum 15 seconds of continuous pedaling
- **Cadence**: Maintain steady, natural rhythm
- **Position**: Consistent cycling position throughout
- **Background**: Clear, uncluttered background

## 🛠️ Advanced Usage

### Custom Analysis
The modular structure allows for easy customization:

```python
from src.analyzers import PedalStrokeAnalyzer, calculate_angle
from src.data import BikeFitManager
from src.utils import angles_from_csv

# Initialize components
analyzer = PedalStrokeAnalyzer()
bike_fit = BikeFitManager()

# Custom analysis workflow
strokes = analyzer.detect_pedal_strokes(knee_angles, timestamps)
fluidity = analyzer.analyze_fluidity(strokes)
```

### Extending Functionality
- Add new analysis modules in `src/analyzers/`
- Extend data management in `src/data/`
- Add utilities in `src/utils/`

## 📚 Documentation

- [Pedal Stroke Analysis Guide](docs/PEDAL_STROKE_ANALYSIS_README.md)
- [API Documentation](src/) - See individual module docstrings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source. See individual files for specific licensing information.

## 🆘 Troubleshooting

### Common Issues

**"No strokes detected"**
- Ensure 15+ seconds of continuous pedaling
- Check camera angle and lighting
- Verify MediaPipe pose detection is working

**Import errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.7+ required)

**Plot saving issues**
- Ensure write permissions in project directory
- Check available disk space

### Getting Help

1. Check the documentation in `docs/`
2. Review the troubleshooting guide
3. Ensure all dependencies are properly installed
4. Verify camera/video file compatibility

## 🎯 Future Enhancements

- Real-time analysis during live sessions
- Historical performance tracking
- Comparison with professional cyclists
- Advanced biomechanical modeling
- Integration with power meters
- Mobile app development

---

**Happy Cycling! 🚴‍♂️🚴‍♀️**

*Built with ❤️ for the cycling community* 