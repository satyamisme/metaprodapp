#   Selenium Appointment Booking Script

This Python script automates appointment booking using Selenium. It reads credentials from `credentials.txt`, checks `booked_slots.txt`, and notifies on booking success.

##   Requirements

* Python 3.x
* Selenium, webdriver-manager (`pip install -r requirements.txt`) [cite: 2]
* Chrome WebDriver
* `credentials.txt` (CivilId=your\_id, Password=your\_password)

##   Setup

1.  **Run `setup_venv.bat`** to:
    * Create a virtual environment. [cite: 3, 4]
    * Install dependencies from `requirements.txt`. [cite: 4]

##   Usage

1.  **Run `start.bat`** to:
    * Activate the virtual environment. [cite: 1]
    * Execute the script (`meta0.1.py`). [cite: 1]

##   Features

* Credential management.
* Booking check.
* Automated booking.
* Success notification (sound).
* Error handling.
