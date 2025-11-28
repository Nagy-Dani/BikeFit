# Pedal Stroke Analysis Feature

## Overview

The BikeFit application now includes advanced **pedal stroke analysis** that evaluates cycling technique by analyzing:

- **Fluidity**: How smooth the transitions are throughout the pedal stroke
- **Smoothness**: Consistency in angular velocity and minimal jerky movements  
- **Cadence Analysis**: Pedaling rhythm and consistency
- **Power Distribution**: How force is applied throughout the stroke cycle
- **Dynamic Visualization**: Real-time plots showing pedaling dynamics
- **Plot Saving**: Automatically saves analysis charts to the "plots" folder

## What's New

### 🆕 Features Added

1. **Pedal Stroke Detection**: Automatically identifies individual pedal strokes from continuous motion
2. **Fluidity Analysis**: Measures smoothness and consistency of pedaling technique
3. **Cadence Tracking**: Calculates RPM and rhythm consistency
4. **Power Distribution Analysis**: Estimates power output throughout the pedal cycle
5. **Dynamic Plotting**: 6 comprehensive visualization charts
6. **Personalized Recommendations**: AI-generated suggestions based on your technique
7. **📁 Plot Saving**: Automatically saves charts as high-resolution PNG files

### 📊 Analysis Metrics

#### Fluidity Scores (0-100%)
- **Overall Fluidity Score**: Weighted combination of all metrics
- **Smoothness**: Based on angular acceleration consistency
- **Consistency**: Stroke-to-stroke variation
- **Velocity Stability**: How steady your pedaling speed is
- **Power Distribution**: Efficiency of force application

#### Dynamics Analysis
- **Average Cadence**: RPM with variability measure
- **Stroke Duration**: Time consistency
- **Angle Range**: Knee angle movement consistency
- **Efficiency Ratings**: Compared to optimal cycling biomechanics

## How It Works

### 1. Data Collection Enhancement
The system now tracks **timestamps** alongside knee and hip angles, enabling:
- Temporal analysis of pedal strokes
- Cadence calculation
- Smoothness assessment
- Dynamic pattern recognition

### 2. Stroke Detection Algorithm
Uses signal processing to:
- Identify peaks and valleys in knee angle data
- Filter out noise and artifacts
- Validate stroke completeness
- Extract individual pedal cycles

### 3. Analysis Pipeline
```
Raw Data → Stroke Detection → Fluidity Analysis → Dynamics Calculation → Visualization → Save to plots/
```

## Using the Feature

### 📹 Video Analysis Mode
1. Check "Test Mode (Use Video File)" in the GUI
2. Select a cycling video (preferably 15+ seconds of continuous pedaling)
3. Ensure clear side view of the cyclist
4. Run the analysis
5. **View and save**: Charts automatically saved to `plots/` folder

### 📷 Live Camera Mode
1. Position camera to capture full leg movement from the side
2. Start the application without test mode
3. Pedal continuously for at least 15 seconds
4. Press ESC to stop recording and analyze
5. **View and save**: Charts automatically saved to `plots/` folder

### 📋 Requirements for Best Results
- **Minimum Duration**: 10-15 seconds of continuous pedaling
- **Camera Angle**: Side view showing full leg movement
- **Consistent Pedaling**: Maintain steady rhythm during recording
- **Good Lighting**: Ensure MediaPipe can detect pose landmarks

## Understanding Your Results

### 🎯 Score Interpretation

| Score Range | Performance | Description |
|-------------|-------------|-------------|
| 80-100% | Excellent | Professional-level technique |
| 60-79% | Good | Solid recreational cyclist |
| 40-59% | Fair | Room for improvement |
| 0-39% | Poor | Focus on basic technique |

### 📈 Visualization Charts

1. **Individual Pedal Strokes**: Overlay of up to 10 individual cycles
2. **Cadence Analysis**: RPM over time with efficiency zones
3. **Fluidity Metrics**: Bar chart of all performance scores
4. **Power Distribution**: Estimated power throughout crank rotation
5. **Angle Progression**: Knee angle changes over time
6. **Summary Dashboard**: Key metrics and recommendations

### 💾 Plot Saving Features

**Automatic Saving:**
- All analysis charts are automatically saved as high-resolution PNG files
- Saved to `plots/` folder in your project directory
- Filename format: `pedal_analysis_[UserName]_[Timestamp].png`
- Example: `pedal_analysis_John_Doe_20240115_143022.png`

**File Details:**
- **Resolution**: 300 DPI for crisp, professional quality
- **Format**: PNG with white background
- **Size**: 16x12 inches (optimized for viewing and printing)
- **Naming**: Includes user name and timestamp for easy identification

### 💡 Sample Recommendations

The system provides personalized suggestions such as:
- "Increase cadence - aim for 80-100 RPM"
- "Focus on maintaining consistent stroke rhythm"
- "Work on smoother pedal transitions"
- "Focus more power on downstroke phase"

## Technical Details

### 🔧 Signal Processing
- **Savitzky-Golay Filtering**: Smooths noisy angle data
- **Peak Detection**: Identifies stroke boundaries
- **Interpolation**: Normalizes strokes for comparison
- **Statistical Analysis**: Calculates variability metrics

### 📊 Biomechanical Calculations
- **Angular Velocity**: Rate of knee angle change
- **Angular Acceleration**: Smoothness indicator
- **Stroke Efficiency**: Comparison to optimal patterns
- **Cadence Efficiency**: Deviation from ideal 80-100 RPM range

### 🎨 Visualization Technology
- **Matplotlib**: High-quality scientific plotting
- **Seaborn**: Statistical visualization enhancements
- **Real-time Display**: Non-blocking plot windows
- **Color Coding**: Performance-based visual feedback
- **Auto-Save**: Plots automatically saved to dedicated folder

## File Management

### 📁 Directory Structure
```
BikeFit/
├── main.py
├── pedal_stroke_analyzer.py
├── plots/                          # ← New: Auto-created plots folder
│   ├── pedal_analysis_User1_20240115_143022.png
│   ├── pedal_analysis_User2_20240115_145530.png
│   └── ...
├── test.csv
└── ...
```

### 🗂️ Plot File Organization
- **Automatic Creation**: `plots/` folder created automatically on first run
- **Unique Names**: Timestamp prevents file conflicts
- **User Identification**: User name included in filename
- **High Quality**: 300 DPI suitable for reports and presentations

## Troubleshooting

### ❌ "No strokes detected"
**Possible causes:**
- Recording too short (< 10 seconds)
- Inconsistent pedaling
- Poor camera angle
- MediaPipe pose detection issues

**Solutions:**
- Record 15+ seconds of continuous pedaling
- Ensure side view captures full leg movement
- Improve lighting conditions
- Maintain steady pedaling rhythm

### ❌ "Insufficient data for analysis"
**Possible causes:**
- Camera not detecting pose landmarks
- Video file format issues
- Very short recording duration

**Solutions:**
- Check camera/video quality
- Use supported video formats (MP4, AVI, MOV)
- Ensure clear view of cyclist's legs

### ❌ Plot saving errors
**Possible causes:**
- Insufficient disk space
- Permission issues
- Invalid characters in user name

**Solutions:**
- Ensure adequate disk space
- Check folder write permissions
- Use simple alphanumeric characters in user names

### ❌ Import/dependency errors
**Solution:**
```bash
pip install -r requirements.txt
```

## Files Added/Modified

### New Files
- `pedal_stroke_analyzer.py`: Core analysis engine with plot saving
- `requirements.txt`: Project dependencies
- `PEDAL_STROKE_ANALYSIS_README.md`: This documentation
- `plots/`: Auto-created directory for saved analysis charts

### Modified Files
- `main.py`: Integrated stroke analysis pipeline with plot handling
- Updated CSV output to include timestamps
- Enhanced both video and live camera modes

## Future Enhancements

Potential improvements for future versions:
- Real-time analysis during live sessions
- Historical performance tracking
- Comparison with professional cyclists
- Advanced biomechanical modeling
- Integration with power meters
- Export capabilities for coaching analysis
- **Plot gallery viewer for saved analyses**
- **Batch processing of multiple videos**

## Support

For questions or issues with the pedal stroke analysis feature:
1. Check this documentation first
2. Verify all dependencies are installed
3. Ensure proper camera setup and lighting
4. Test with known good video files
5. Check `plots/` folder for saved charts

---

**Happy Cycling! 🚴‍♂️🚴‍♀️** 