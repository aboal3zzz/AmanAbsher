# AmanAbsher – Dynamic Risk-Based Login Engine

Hackathon prototype of a **dynamic risk engine** for Absher-style logins.  
The system evaluates every login attempt in real time using multiple signals  
(location, device, network, behaviour, and time) and then decides whether to:

- Allow the login directly
- Block the login as high-risk :contentReference[oaicite:0]{index=0}

---

## 1. Project Idea

Traditional login systems usually check only the username and password.  
**AmanAbsher** adds an extra intelligence layer that estimates how risky  
each login attempt is.

The risk engine looks at five main axes:

1. **Location** – country, city, GPS / zone (home, office, unusual place).
2. **Device** – trusted device or not, rooted / jailbroken, old OS, etc.
3. **Network** – home Wi-Fi vs public Wi-Fi vs mobile data, VPN usage.
4. **User behaviour** – typing speed, number of failed attempts, patterns.
5. **Time of login** – normal time for the user vs unusual time (e.g. 3 AM). :contentReference[oaicite:1]{index=1}  

Using these signals, the engine calculates a **risk score** and picks the
appropriate action (allow / step-up verification / block).

---

## 2. How the System Works (Overview)

- The user opens the login page.
- The system collects information about:
  - Current location / zone
  - Device and browser
  - Network type and VPN
  - Behavioural signals (failed attempts, typing)
  - Time of the attempt
- All signals are passed to the **risk engine**.
- The risk engine returns:
  - A risk score (0–100)
  - A decision: `ALLOW`, `CHALLENGE`, or `BLOCK`.
- The UI then:
  - Logs the user in directly, **or**
  - Asks for extra verification, **or**
  - Shows a warning and blocks the login.

---

## 3. Demo Credentials

To make testing easy during the hackathon, the prototype has a fixed demo user:

- **Username:** `Salman`  
- **Password:** `1234`

Use these credentials on the login screen to test how the risk engine reacts.

---

## 4. Project Structure (Python side)

The main files in the repo are:

- `app.py`  
  Main application entry point, defines the web server and routes  
  (`/login`, `/dashboard`, etc.).

- `models.py`  
  Contains the data models (User, LoginAttempt) using SQLAlchemy.

- `risk_engine.py`  
  Contains the core logic that calculates the risk score based on  
  location, device, network, behaviour, and time signals.

- `requirements.txt`  
  Python dependencies (for example: `flask`, `flask_sqlalchemy`).

---

## 5. How to Run the Project

### Prerequisites

- Python 3.x installed
- `pip` installed

### Setup & Run (development mode)

```bash
# 1. Clone the repository
git clone https://github.com/aboal3zzz/AmanAbsher.git
cd AmanAbsher

# 2.  Create and activate a virtual environment
python -m venv venv
# On macOS / Linux:
source venv/bin/activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
