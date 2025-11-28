"""
This module contains the GUI for the BikeFit application.
"""
import tkinter as tk
from tkinter import messagebox

def collect_user_data_gui():
    """Collect user data through a more robust GUI interface"""
    def submit_data():
        try:
            # Create a dictionary to hold the new user data
            new_user_data = {
                'name': name_entry.get() or 'Average Joe',
                'bike_type': bike_type.get(),
                'test_mode': test_mode_var.get()
            }

            # List of numeric fields to validate
            numeric_fields = {
                'height_cm': height_entry,
                'inseam_cm': inseam_entry,
                'arm_length_cm': arm_length_entry,
                'torso_length_cm': torso_length_entry,
                'saddle_height_cm': saddle_height_entry,
                'handlebar_reach_cm': handlebar_reach_entry,
                'handlebar_width_cm': handlebar_width_entry,
                'stack_height_cm': stack_height_entry,
                'stack_angle': stack_angle_entry
            }

            # Validate and convert each numeric field
            for key, entry_widget in numeric_fields.items():
                value_str = entry_widget.get()
                if not value_str: # Treat empty as 0
                    new_user_data[key] = 0.0
                else:
                    new_user_data[key] = float(value_str)

            # If all conversions are successful, update the main dictionary and close
            new_user.update(new_user_data)
            messagebox.showinfo("Data Collected", "User data successfully collected!")
            root.destroy()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all numeric fields.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred: {e}")

    root = tk.Tk()
    root.title("BikeFit - Advanced Bicycle Fitting")
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
