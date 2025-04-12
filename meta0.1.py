import time
import re
import threading
import platform
import os
if platform.system() == "Windows":
    import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

BOOKING_URL = 'https://metaprodapp.azurewebsites.net/en/Appointments/Apply?ServiceId=1367&DepartmentId=347'

def read_credentials():
    try:
        with open('credentials.txt', 'r') as file:
            lines = file.readlines()
        credentials = {}
        for line in lines:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                credentials[key] = value
            else:
                raise ValueError("Invalid format")
        civil_id = credentials.get('CivilId', '').strip()
        password = credentials.get('Password', '').strip()
        if not re.match(r'^\d{12}$', civil_id):
            raise ValueError("Civil ID must be 12 digits")
        if not password:
            raise ValueError("Password cannot be empty")
        return civil_id, password
    except (FileNotFoundError, ValueError) as e:
        print(f"Credentials error: {e}")
        exit(1)

def check_booked_slots(civil_id):
    try:
        with open('booked_slots.txt', 'r') as file:
            return any(f"CivilID={civil_id}" in line for line in file)
    except FileNotFoundError:
        return False

def save_booked_slot(civil_id, date, slot_time):
    try:
        with open('booked_slots.txt', 'a') as file:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"CivilID={civil_id},Date={date},Time={slot_time},BookedAt={timestamp}\n")
        print(f"Saved: {civil_id}, {date}, {slot_time}")
    except Exception as e:
        print(f"Save failed: {e}")

def play_continuous_sound(stop_event):
    try:
        start_time = time.time()
        os_type = platform.system()
        while not stop_event.is_set() and (time.time() - start_time) < 300:  # 5 minutes
            if os_type == "Windows":
                winsound.Beep(500, 500)  # 500Hz, 500ms
                time.sleep(0.5)  # 1s cycle
            elif os_type == "Darwin":
                os.system('afplay /System/Library/Sounds/Glass.aiff')  # ~1s sound
                time.sleep(0.5)  # 1.5s cycle
            else:
                print("No sound support")
                time.sleep(1)
    except Exception as e:
        print(f"Sound error: {e}")

def notify_success():
    print("*** BOOKING SUCCESSFUL ***")
    stop_event = threading.Event()
    sound_thread = threading.Thread(target=play_continuous_sound, args=(stop_event,))
    sound_thread.daemon = True
    sound_thread.start()
    return stop_event

def login(driver, wait, civil_id, password, is_relogin=False):
    max_attempts = 2 if not is_relogin else 1
    for attempt in range(max_attempts):
        try:
            if is_relogin:
                print("Relogin attempt...")
            civil_id_input = wait.until(EC.presence_of_element_located((By.NAME, 'CivilId')))
            civil_id_input.clear()
            civil_id_input.send_keys(civil_id)
            password_input = wait.until(EC.presence_of_element_located((By.NAME, 'Password')))
            password_input.clear()
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(1.5)
            try:
                driver.find_element(By.CSS_SELECTOR, '#days-tab a.nav-link')
                if is_relogin:
                    print("Relogin OK")
                return True
            except NoSuchElementException:
                try:
                    error = driver.find_element(By.CSS_SELECTOR, '.error-message, .alert-danger').text
                    print(f"Login failed: {error}")
                    return False
                except NoSuchElementException:
                    print("Login failed: No redirect")
                    if attempt + 1 < max_attempts:
                        driver.refresh()
                        time.sleep(1)
        except (TimeoutException, NoSuchElementException):
            if attempt + 1 < max_attempts:
                print(f"Login attempt {attempt + 1} failed")
                driver.refresh()
                time.sleep(1)
            else:
                print("Login failed")
                return False
        except UnexpectedAlertPresentException as e:
            print(f"Alert: {e.alert_text}")
            driver.switch_to.alert.accept()
            return False
    return False

def ensure_booking_page(driver):
    if driver.current_url != BOOKING_URL:
        print(f"Detected navigation away, redirecting to booking page from {driver.current_url}")
        driver.get(BOOKING_URL)
        time.sleep(1)

def main():
    driver = None
    sound_stop_event = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        wait = WebDriverWait(driver, 8)

        civil_id, password = read_credentials()
        if check_booked_slots(civil_id):
            print("Existing booking found")
            return

        driver.get(BOOKING_URL)

        if not login(driver, wait, civil_id, password):
            print("Login stopped")
            return

        slot_found = False
        refresh_count = 0

        while True:
            try:
                refresh_count = 0
                tabs = driver.find_elements(By.CSS_SELECTOR, '#days-tab a.nav-link')
                if not tabs:
                    print("No tabs, refresh in 8s")
                    time.sleep(8)
                    ensure_booking_page(driver)
                    driver.refresh()
                    continue

                for tab in tabs[::-1]:
                    try:
                        tab.click()
                        time.sleep(0.3)
                        date_text = tab.text
                        buttons = driver.find_elements(By.CSS_SELECTOR, '.btn-apply-appointment')
                        for button in buttons:
                            try:
                                badge = button.find_element(By.CSS_SELECTOR, '.badge-primary')
                                if "0 booked" in badge.text.lower():
                                    print(f"Slot: {button.text} on {date_text}")
                                    button.click()
                                    time.sleep(0.3)
                                    yes_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-success')))
                                    yes_button.click()
                                    time.sleep(1.5)
                                    print("Booked!")
                                    slot_found = True
                                    save_booked_slot(civil_id, date_text, button.text)
                                    sound_stop_event = notify_success()
                                    break
                            except NoSuchElementException:
                                continue
                        if slot_found:
                            break
                    except Exception as e:
                        print(f"Tab error: {e}")
                        continue
                if slot_found:
                    break

                time.sleep(1 if "0 booked" in driver.page_source.lower() else 8)
                ensure_booking_page(driver)
                driver.refresh()

            except Exception as e:
                print(f"Error: {e}")
                refresh_count += 1
                if refresh_count >= 2:
                    ensure_booking_page(driver)
                    if not login(driver, wait, civil_id, password, is_relogin=True):
                        if refresh_count >= 3:
                            print("Too many failures")
                            break
                    refresh_count = 0
                    driver.get(BOOKING_URL)
                else:
                    time.sleep(8)
                    ensure_booking_page(driver)
                    driver.refresh()

    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        if sound_stop_event:
            sound_stop_event.set()
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()