# Blood Donation Web Application - Specification

## 1. Project Overview

**Project Name:** LifeFlow - Blood Donation System  
**Project Type:** Full-stack Web Application  
**Core Functionality:** A comprehensive blood donation platform enabling donor registration, blood group search, emergency requests, and AI-powered donor-patient matching based on location and blood compatibility.  
**Target Users:** Blood donors, patients in need, hospitals, and blood banks

---

## 2. Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Database:** SQLite (file-based for simplicity)
- **AI Matching:** Python-based algorithm with location proximity and blood type compatibility scoring

---

## 3. UI/UX Specification

### Layout Structure

**Pages:**
1. **Home Page** - Landing page with hero section and quick actions
2. **Donor Registration** - Form for new donor signup
3. **Blood Search** - Search blood by group and location
4. **Emergency Request** - Post emergency blood needs
5. **AI Match** - View AI-suggested donor matches

**Common Layout:**
- Fixed Navigation Bar (top)
- Main Content Area
- Footer (bottom)

### Visual Design

**Color Palette:**
- Primary: `#E63946` (Blood Red)
- Secondary: `#1D3557` (Deep Navy)
- Accent: `#F4A261` (Warm Orange)
- Background: `#F1FAEE` (Off-White)
- Text Primary: `#1D3557`
- Text Secondary: `#457B9D`
- Success: `#2A9D8F`
- Warning: `#E9C46A`

**Typography:**
- Headings: 'Playfair Display', serif
- Body: 'Source Sans Pro', sans-serif
- Font Sizes:
  - H1: 2.5rem
  - H2: 2rem
  - H3: 1.5rem
  - Body: 1rem
  - Small: 0.875rem

**Spacing System:**
- Base unit: 8px
- Margins: 16px, 24px, 32px, 48px
- Paddings: 8px, 16px, 24px, 32px

**Visual Effects:**
- Card shadows: `0 4px 20px rgba(0,0,0,0.1)`
- Hover transitions: 0.3s ease
- Button hover: scale(1.02) with shadow increase
- Page load animations: fade-in-up

### Components

**Navigation Bar:**
- Logo (left)
- Nav links: Home, Register as Donor, Search Blood, Emergency, AI Match
- Mobile: Hamburger menu

**Hero Section:**
- Full-width background with gradient overlay
- Headline and subheadline
- CTA buttons

**Forms:**
- Floating labels
- Input validation with visual feedback
- Submit button with loading state

**Cards:**
- Donor cards with avatar, name, blood group, location
- Request cards with status badge
- Match score indicator

**Buttons:**
- Primary: Red background, white text
- Secondary: Navy background, white text
- Outline: Transparent with border

---

## 4. Functionality Specification

### Core Features

#### 4.1 Donor Registration
- Fields: Name, Email, Phone, Blood Group (dropdown), Date of Birth, Gender, Address (City, State), Pincode
- Validation: All fields required, email format, phone format
- Storage: SQLite database

#### 4.2 Blood Search
- Search by: Blood Group (required), City (optional), State (optional)
- Display: List of matching donors with contact options
- Sort by: Location proximity (if location provided)

#### 4.3 Emergency Request
- Fields: Patient Name, Required Blood Group, Units Needed, Hospital Name, Hospital Address, Contact Person, Phone, Urgency Level, Required Date
- Display: Public feed of emergency requests
- Notification: Show matching donors

#### 4.4 AI-Based Matching
- Algorithm Factors:
  - Blood type compatibility (weight: 40%)
  - Location proximity (weight: 35%)
  - Last donation date (weight: 15%)
  - Donor availability status (weight: 10%)
- Compatibility Matrix:
  - O- can donate to all
  - O+ can donate to O+, A+, B+, AB+
  - A- can donate to A-, A+, AB-, AB+
  - A+ can donate to A+, AB+
  - B- can donate to B-, B+, AB-, AB+
  - B+ can donate to B+, AB+
  - AB- can donate to AB-, AB+
  - AB+ can donate to AB+
- Output: Ranked list of donors with match score percentage

### User Interactions
- Form submissions with AJAX
- Real-time search results
- Modal for donor contact details
- Toast notifications for actions

### Data Handling
- SQLite database with tables:
  - donors (id, name, email, phone, blood_group, dob, gender, city, state, pincode, last_donation, created_at)
  - emergency_requests (id, patient_name, blood_group, units, hospital, address, contact_person, phone, urgency, required_date, created_at)

---

## 5. Page Specifications

### 5.1 Home Page (index.html)
- Hero section with "Donate Blood, Save Life" message
- Quick stats: Total donors, Active requests
- Three feature cards: Register, Search, Emergency
- How it works section

### 5.2 Donor Registration (register.html)
- Multi-section form or single page form
- Blood group selector with visual blood drop icons
- Terms and conditions checkbox
- Success modal on completion

### 5.3 Blood Search (search.html)
- Search form with filters
- Results grid with donor cards
- Map view toggle (optional)

### 5.4 Emergency Requests (emergency.html)
- Post request form
- Active requests feed
- Filter by blood group, urgency

### 5.5 AI Match (ai-match.html)
- Patient/Request selector
- Match results with score visualization
- Detailed donor info

---

## 6. API Endpoints (Flask)

```
GET  /api/donors                 - Get all donors (with filters)
POST /api/donors                 - Register new donor
GET  /api/donors/<id>            - Get donor by ID
GET  /api/search                 - Search donors by blood group & location
GET  /api/emergency-requests     - Get all emergency requests
POST /api/emergency-requests     - Create emergency request
GET  /api/ai-match/<request_id>  - Get AI-matched donors for a request
```

---

## 7. Acceptance Criteria

1. ✓ Home page loads with hero section and navigation
2. ✓ Donor registration form validates and stores data
3. ✓ Blood search returns correct donors by blood group
4. ✓ Emergency requests can be created and displayed
5. ✓ AI matching returns ranked donors with compatibility scores
6. ✓ Responsive design works on mobile and desktop
7. ✓ All API endpoints return proper JSON responses
8. ✓ Database persists data between sessions
