import csv
import os
from datetime import datetime

class BikeFitManager:
    def __init__(self, filename="bike_fit_data.csv"):
        self.filename = filename
        # Define CSV headers specific to bike fitting
        
        self.headers = [
            'user_id', 'date_added', 'name', 'height_cm',
            'inseam_cm', 'arm_length_cm', 'torso_length_cm','bike_type',
            'saddle_height_cm', 'handlebar_reach_cm', 'handlebar_width_cm',
            'stack_height_cm', 'stack_angle',
            'knee_angle_0', 'knee_angle_6', 'knee_angle_average', 
            'hip_angle_0', 'hip_angle_6', 'hip_angle_average'
        ]
        # Create file with headers if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writeheader()

    def add_user(self, user_data):
        """Add a new user with their bike fit measurements"""
        # Add timestamp and generate simple user_id
        user_data['date_added'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_data['user_id'] = self._generate_user_id()
        
        # Filter out any fields not in headers
        filtered_data = {k: v for k, v in user_data.items() if k in self.headers}
        
        with open(self.filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writerow(filtered_data)
        print(f"Added user {user_data['name']} with ID {user_data['user_id']}")

    def get_user(self, user_id):
        """Retrieve user data by ID"""
        with open(self.filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['user_id'] == str(user_id):
                    return row
        return None

    def update_user(self, user_id, new_data):
        """Update existing user data"""
        all_data = self._read_all_data()
        updated = False
        
        for i, row in enumerate(all_data):
            if row['user_id'] == str(user_id):
                all_data[i].update(new_data)
                updated = True
                break
                
        if updated:
            self._write_all_data(all_data)
            print(f"Updated user {user_id}")
        else:
            print(f"User {user_id} not found")

    def delete_user(self, user_id):
        """Delete a user by ID"""
        all_data = self._read_all_data()
        initial_length = len(all_data)
        all_data = [row for row in all_data if row['user_id'] != str(user_id)]
        
        if len(all_data) < initial_length:
            self._write_all_data(all_data)
            print(f"Deleted user {user_id}")
        else:
            print(f"User {user_id} not found")

    def list_all_users(self):
        """List all users in the database"""
        with open(self.filename, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def _generate_user_id(self):
        """Generate a simple incremental user ID"""
        all_data = self._read_all_data()
        return len(all_data) + 1

    def _read_all_data(self):
        """Helper method to read all CSV data"""
        with open(self.filename, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def _write_all_data(self, data):
        """Helper method to write all data back to CSV"""
        with open(self.filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(data)