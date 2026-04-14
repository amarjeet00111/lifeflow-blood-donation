from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = 'blood_donation.db'

# Blood group compatibility matrix (who can donate to whom)
COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+']
}

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Donors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT,
            last_donation TEXT,
            available INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Emergency requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            units INTEGER NOT NULL,
            hospital_name TEXT NOT NULL,
            hospital_address TEXT,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL,
            urgency TEXT NOT NULL,
            required_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Home page"""
    conn = get_db_connection()
    donor_count = conn.execute('SELECT COUNT(*) FROM donors').fetchone()[0]
    request_count = conn.execute("SELECT COUNT(*) FROM emergency_requests WHERE status = 'active'").fetchone()[0]
    conn.close()
    return render_template('index.html', donor_count=donor_count, request_count=request_count)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/emergency')
def emergency():
    conn = get_db_connection()
    requests = conn.execute('''
        SELECT * FROM emergency_requests 
        WHERE status = 'active' 
        ORDER BY 
            CASE urgency 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'normal' THEN 3 
            END,
            created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('emergency.html', requests=requests)

@app.route('/ai-match')
def ai_match():
    conn = get_db_connection()
    requests = conn.execute('''
        SELECT * FROM emergency_requests 
        WHERE status = 'active' 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('ai_match.html', requests=requests)

# API Endpoints

@app.route('/api/donors', methods=['GET', 'POST'])
def handle_donors():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            conn.execute('''
                INSERT INTO donors (name, email, phone, blood_group, dob, gender, city, state, pincode, last_donation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'], data['email'], data['phone'], data['blood_group'],
                data.get('dob'), data.get('gender'), data['city'], data['state'],
                data.get('pincode'), data.get('last_donation')
            ))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Donor registered successfully!'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered!'}), 400
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    donors = conn.execute('SELECT * FROM donors ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in donors])

@app.route('/api/search', methods=['GET'])
def search_donors():
    blood_group = request.args.get('blood_group')
    city = request.args.get('city', '')
    state = request.args.get('state', '')
    
    query = 'SELECT * FROM donors WHERE blood_group = ? AND available = 1'
    params = [blood_group]
    
    if city:
        query += ' AND city LIKE ?'
        params.append(f'%{city}%')
    if state:
        query += ' AND state LIKE ?'
        params.append(f'%{state}%')
    
    query += ' ORDER BY created_at DESC'
    
    conn = get_db_connection()
    donors = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in donors])

@app.route('/api/emergency-requests', methods=['GET', 'POST'])
def handle_emergency_requests():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            conn.execute('''
                INSERT INTO emergency_requests 
                (patient_name, blood_group, units, hospital_name, hospital_address, contact_person, phone, urgency, required_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['patient_name'], data['blood_group'], data['units'],
                data['hospital_name'], data.get('hospital_address'),
                data['contact_person'], data['phone'], data['urgency'],
                data.get('required_date')
            ))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Emergency request posted successfully!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    requests = conn.execute('''
        SELECT * FROM emergency_requests 
        WHERE status = 'active' 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in requests])

@app.route('/api/emergency-requests/<int:request_id>', methods=['PUT', 'DELETE'])
def update_emergency_request(request_id):
    """Update or cancel an emergency request"""
    conn = get_db_connection()
    
    # Check if request exists
    req = conn.execute('SELECT * FROM emergency_requests WHERE id = ?', (request_id,)).fetchone()
    if not req:
        conn.close()
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'update')
    
    try:
        if action == 'cancel':
            # Cancel the request
            conn.execute('UPDATE emergency_requests SET status = ? WHERE id = ?', ('cancelled', request_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Request cancelled successfully!'})
        
        elif action == 'complete':
            # Mark as completed (blood collected)
            conn.execute('UPDATE emergency_requests SET status = ? WHERE id = ?', ('completed', request_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Request marked as completed!'})
        
        elif action == 'update':
            # Update request details
            conn.execute('''
                UPDATE emergency_requests 
                SET patient_name = ?, blood_group = ?, units = ?, hospital_name = ?,
                    hospital_address = ?, contact_person = ?, phone = ?, urgency = ?, required_date = ?
                WHERE id = ?
            ''', (
                data.get('patient_name', req['patient_name']),
                data.get('blood_group', req['blood_group']),
                data.get('units', req['units']),
                data.get('hospital_name', req['hospital_name']),
                data.get('hospital_address', req['hospital_address']),
                data.get('contact_person', req['contact_person']),
                data.get('phone', req['phone']),
                data.get('urgency', req['urgency']),
                data.get('required_date', req['required_date']),
                request_id
            ))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Request updated successfully!'})
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ai-match/<int:request_id>', methods=['GET'])
def ai_match_donors(request_id):
    """AI-powered donor matching based on multiple factors"""
    conn = get_db_connection()
    
    # Get the emergency request
    req = conn.execute('SELECT * FROM emergency_requests WHERE id = ?', (request_id,)).fetchone()
    if not req:
        conn.close()
        return jsonify({'error': 'Request not found'}), 404
    
    required_blood = req['blood_group']
    hospital_address = req['hospital_address'] if req['hospital_address'] else ''
    
    # Get all available donors
    donors = conn.execute('SELECT * FROM donors WHERE available = 1').fetchall()
    
    # Calculate match scores
    matches = []
    for donor in donors:
        score = 0
        details = {}
        
        # Blood type compatibility (40% weight)
        if required_blood in COMPATIBILITY.get(donor['blood_group'], []):
            blood_score = 40
            if donor['blood_group'] == required_blood:
                blood_score = 40
            elif donor['blood_group'] in ['O-', 'O+']:
                blood_score = 35
            else:
                blood_score = 30
            score += blood_score
            details['blood_compatible'] = True
        else:
            details['blood_compatible'] = False
            continue
        
        # Location proximity (35% weight)
        city_match = False
        if hospital_address:
            city_match = donor['city'].lower() in hospital_address.lower()
        
        if city_match:
            score += 35
            details['location_score'] = 'Same City'
        else:
            score += 5
            details['location_score'] = 'Different Location'
        
        # Last donation date (15% weight)
        if donor['last_donation']:
            try:
                last_don = datetime.strptime(donor['last_donation'], '%Y-%m-%d')
                days_since = (datetime.now() - last_don).days
                if days_since >= 90:
                    if days_since >= 180:
                        score += 15
                        details['donation_ready'] = 'Ready (6+ months)'
                    else:
                        score += 10
                        details['donation_ready'] = 'Ready (3-6 months)'
                else:
                    score += 0
                    details['donation_ready'] = 'Not ready'
            except:
                score += 7
                details['donation_ready'] = 'Unknown'
        else:
            score += 15
            details['donation_ready'] = 'First time donor'
        
        # Availability status (10% weight)
        score += 10 if donor['available'] else 0
        
        # Cap score at 100
        score = min(score, 100)
        
        matches.append({
            'donor': dict(donor),
            'score': score,
            'details': details
        })
    
    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    conn.close()
    
    return jsonify({
        'request': dict(req),
        'matches': matches[:10]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
