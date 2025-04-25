import tkinter as tk
from tkinter import simpledialog, messagebox

def start_application():
    # Start your main application loop here
    #main()
    pass

def collect_user_data_gui():
    def submit_data():
        new_user['name'] = name_entry.get()
        new_user['height_cm'] = float(height_entry.get())
        new_user['bike_type'] = bike_type.get()
        new_user['inseam_cm'] = float(inseam_entry.get())
        new_user['arm_length_cm'] = float(arm_length_entry.get())
        new_user['torso_length_cm'] = float(torso_length_entry.get())
        new_user['saddle_height_cm'] = float(saddle_height_entry.get())
        new_user['handlebar_reach_cm'] = float(handlebar_reach_entry.get())
        new_user['handlebar_width_cm'] = float(handlebar_width_entry.get())
        new_user['stack_height_cm'] = float(stack_height_entry.get())
        new_user['stack_angle'] = float(stack_angle_entry.get())
        messagebox.showinfo("Data Collected", "User data successfully collected!")
        root.destroy()

    root = tk.Tk()
    root.title("Bike Fitting App")
    new_user = {}

    tk.Label(root, text="Name").grid(row=0)
    tk.Label(root, text="Height (cm)").grid(row=1)
    tk.Label(root, text="Bike Type").grid(row=2)

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
    tk.OptionMenu(root, bike_type, "Road", "Mountain", "Hybrid", "TT").grid(row=2, column=1)

    name_entry.grid(row=0, column=1)
    height_entry.grid(row=1, column=1)
    inseam_entry.grid(row=2, column=1)
    arm_length_entry.grid(row=3, column=1)
    torso_length_entry.grid(row=4, column=1)
    saddle_height_entry.grid(row=5, column=1)
    handlebar_reach_entry.grid(row=6, column=1)
    handlebar_width_entry.grid(row=7, column=1)
    stack_height_entry.grid(row=8, column=1)
    stack_angle_entry.grid(row=9, column=1)
    

    tk.Button(root, text="Submit", command=submit_data).grid(row=3, column=1)
    root.mainloop()

    return new_user  # Return the inputted user data