"""
Setup script to create a SQLite database with dummy appointment data.
Run this file once to create the database with sample data.

This creates a simple appointments database with:
- Doctors table (doctor information)
- Appointments table (patient appointments with token numbers)
"""

import sqlite3
from datetime import datetime, timedelta

def create_database():
    """
    Create SQLite database with doctors and appointments tables.
    Populates with dummy data for testing.
    """
    
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (for clean setup)
    cursor.execute('DROP TABLE IF EXISTS appointments')
    cursor.execute('DROP TABLE IF EXISTS doctors')
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY,
            doctor_name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            available_days TEXT NOT NULL
        )
    ''')
    
    # Create appointments table
    cursor.execute('''
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            token_number INTEGER NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
    ''')
    
    # Insert dummy doctor data
    doctors_data = [
        (1, 'Dr. Harshin', 'General Medicine', 'Monday to Friday'),
        (2, 'Dr. Priya Sharma', 'Pediatrics', 'Monday, Wednesday, Friday')
    ]
    
    cursor.executemany('''
        INSERT INTO doctors (doctor_id, doctor_name, specialization, available_days)
        VALUES (?, ?, ?, ?)
    ''', doctors_data)
    
    # Generate dummy appointment data for today and next few days
    today = datetime.now()
    appointments_data = []
    
    # Appointments for Dr. Harshin (doctor_id = 1)
    dr_harshin_appointments = [
        (1, 'Rajesh Kumar', 1, today.strftime('%Y-%m-%d'), '09:00 AM', 'Scheduled'),
        (1, 'Priya Singh', 2, today.strftime('%Y-%m-%d'), '09:30 AM', 'Scheduled'),
        (1, 'Amit Patel', 3, today.strftime('%Y-%m-%d'), '10:00 AM', 'Completed'),
        (1, 'Sneha Reddy', 4, today.strftime('%Y-%m-%d'), '10:30 AM', 'Scheduled'),
        (1, 'Vikram Mehta', 5, today.strftime('%Y-%m-%d'), '11:00 AM', 'Scheduled'),
        (1, 'Anjali Gupta', 6, (today + timedelta(days=1)).strftime('%Y-%m-%d'), '09:00 AM', 'Scheduled'),
        (1, 'Rahul Verma', 7, (today + timedelta(days=1)).strftime('%Y-%m-%d'), '09:30 AM', 'Scheduled'),
    ]
    
    # Appointments for Dr. Priya Sharma (doctor_id = 2)
    dr_priya_appointments = [
        (2, 'Baby Aisha', 1, today.strftime('%Y-%m-%d'), '10:00 AM', 'Scheduled'),
        (2, 'Baby Rohan', 2, today.strftime('%Y-%m-%d'), '10:30 AM', 'Scheduled'),
        (2, 'Baby Kavya', 3, today.strftime('%Y-%m-%d'), '11:00 AM', 'Completed'),
        (2, 'Baby Arjun', 4, today.strftime('%Y-%m-%d'), '11:30 AM', 'Scheduled'),
        (2, 'Baby Diya', 5, (today + timedelta(days=2)).strftime('%Y-%m-%d'), '10:00 AM', 'Scheduled'),
    ]
    
    # Combine all appointments
    appointments_data = dr_harshin_appointments + dr_priya_appointments
    
    # Insert appointment data
    cursor.executemany('''
        INSERT INTO appointments (doctor_id, patient_name, token_number, appointment_date, appointment_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', appointments_data)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print("📊 Database file: hospital.db")
    print(f"👨‍⚕️ Doctors added: {len(doctors_data)}")
    print(f"📅 Appointments added: {len(appointments_data)}")
    print("\nYou can now run the FastAPI server to use the SQL agent!")

if __name__ == "__main__":
    create_database()