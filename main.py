#!/usr/bin/env python3
"""
BikeFit - Advanced Bicycle Fitting Application (PySide6 Edition)
"""
import sys
from src.ui.main_window import run_gui

def main():
    """Main application entry point"""
    print("Starting BikeFit Pro (Qt Version)...")
    try:
        run_gui()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
