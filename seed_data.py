"""
Data Seeding Script for LifeFlow Blood Donation App
Run this script to add sample hospitals and donors to the database
"""

import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'blood_donation.db'

# Sample hospitals data
HOSPITALS = [
    {"name": "City General Hospital", "city": "Mumbai", "state": "Maharashtra", "address": "Fort Area, Mumbai Central"},
    {"name": "Apollo Hospital", "city": "Delhi", "state": "Delhi", "address": "Sarita Vihar, Delhi"},
    {"name": "Christian Medical College", "city": "Vellore", "state": "Tamil Nadu", "address": "Vellore Town"},
    {"name": "All India Institute of Medical Sciences", "city": "Delhi", "state": "Delhi", "address": "Ansari Nagar"},
    {"name": "Fortis Hospital", "city": "Bangalore", "state": "Karnataka", "address": "Cantonment, Bangalore"},
    {"name": "Medanta Hospital", "city": "Gurgaon", "state": "Haryana", "address": "Sector 38, Gurgaon"},
    {"name": "Kokilaben Hospital", "city": "Mumbai", "state": "Maharashtra", "address": "Andheri West"},
    {"name": "Narayana Health", "city": "Bangalore", "state": "Karnataka", "address": "Bommasandra, Bangalore"},
    {"name": "Manipal Hospital", "city": "Bangalore", "state": "Karnataka", "address": "Old Airport Road"},
    {"name": "Max Hospital", "city": "Delhi", "state": "Delhi", "address": "Saket, Delhi"},
]

# Sample donor names
FIRST_NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Raj", "Kavita", "Sanjay", "Meera", "Deepak", "Pooja", "Arun", "Divya", "Kiran", "Lakshmi"]
LAST_NAMES = ["Sharma", "Patel", "Singh", "Kumar", "Joshi", "Reddy", "Gupta", "Agarwal", "Mehta", "Shah", "Verma", "Iyer", "Nair", "Mishra", "Chowdhury"]

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

CITIES_STATES = [
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Bangalore", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"),
    ("Hyderabad", "Telangana"),
    ("Pune", "Maharashtra"),
    ("Gurgaon", "Haryana"),
    ("Chandigarh", "Punjab"),
    ("Ahmedabad", "Gujarat"),
    ("Abohar", "Punjab"),
    ("Ludhiana", "Punjab"),
    ("Jalandhar", "Punjab"),
]

def seed_hospitals():
    """Add sample hospitals to emergency_requests table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if we already have hospitals
    cursor.execute("SELECT COUNT(*) FROM emergency_requests")
    if cursor.fetchone()[0] > 0:
        print("Hospital data already exists!")
        conn.close()
        return
    
    # Add sample emergency requests (simulating hospital needs)
    statuses = ["critical", "high", "normal"]
    
    for hospital in HOSPITALS:
        for _ in range(2):  # 2 requests per hospital
            patient_name = f"Patient_{random.randint(1000, 9999)}"
            blood_group = random.choice(BLOOD_GROUPS)
            units = random.randint(1, 4)
            urgency = random.choice(statuses)
            required_date = (datetime.now() + timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO emergency_requests 
                (patient_name, blood_group, units, hospital_name, hospital_address, contact_person, phone, urgency, required_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_name, blood_group, units, 
                hospital['name'], hospital['address'],
                f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                f"+91{random.randint(9000000000, 9999999999)}",
                urgency, required_date
            ))
    
    conn.commit()
    conn.close()
    print(f"Added {len(HOSPITALS) * 2} hospital emergency requests!")

def seed_donors():
    """Add sample donors to the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if we already have many donors (add more if less than 20)
    cursor.execute("SELECT COUNT(*) FROM donors")
    current_count = cursor.fetchone()[0]
    
    if current_count >= 20:
        print(f"Donor data already exists! ({current_count} donors)")
        conn.close()
        return
    
    # Add sample donors
    for _ in range(50):  # 50 sample donors
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = f"{name.lower().replace(' ', '.')}{random.randint(1, 999)}@email.com"
        phone = f"+91{random.randint(9000000000, 9999999999)}"
        blood_group = random.choice(BLOOD_GROUPS)
        
        city, state = random.choice(CITIES_STATES)
        
        # Random date of birth (between 18 and 55 years old)
        age = random.randint(18, 55)
        dob_year = datetime.now().year - age
        dob = f"{random.randint(1, 12):02d}-{random.randint(1, 28):02d}-{dob_year}"
        
        gender = random.choice(["male", "female", "other"])
        
        # Last donation date (some donors, some not)
        last_donation = ""
        if random.random() > 0.3:  # 70% have donated before
            days_ago = random.randint(30, 365)
            last_donation = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO donors (name, email, phone, blood_group, dob, gender, city, state, last_donation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, blood_group, dob, gender, city, state, last_donation))
    
    conn.commit()
    conn.close()
    print("Added 50 sample donors!")

def show_stats():
    """Display database statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM donors")
    donor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM emergency_requests")
    request_count = cursor.fetchone()[0]
    
    print(f"\n=== Database Stats ===")
    print(f"Total Donors: {donor_count}")
    print(f"Total Emergency Requests: {request_count}")
    
    # Blood group distribution
    print(f"\nDonors by Blood Group:")
    cursor.execute("SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group ORDER BY blood_group")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    print("Seeding data for LifeFlow Blood Donation App...\n")
    seed_hospitals()
    seed_donors()
    show_stats()
    print("\nData seeding completed!")
