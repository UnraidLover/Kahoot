import time
import random
import threading
import signal
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

game_pin = input("Enter Kahoot Game PIN: ")
username_base = input("Enter base username (Max 12 chars): ")[:12]
num_bots = int(input("Enter the number of bots: "))

chrome_driver_path = "chromedriver.exe"
chrome_binary_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

drivers = []

def close_all_browsers(signal_received=None, frame=None):
    print("\nShutting down. Closing all Chrome tabs...")
    for driver in drivers:
        try:
            driver.quit()
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, close_all_browsers)
signal.signal(signal.SIGTERM, close_all_browsers)

def start_bot(bot_number):
    username = f"{username_base}{bot_number}"[:12]
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            service = Service(chrome_driver_path)
            options = webdriver.ChromeOptions()
            options.binary_location = chrome_binary_path
            options.add_argument("--incognito")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")

            driver = webdriver.Chrome(service=service, options=options)
            drivers.append(driver)

            driver.get("https://kahoot.it")

            pin_input = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Game PIN']"))
            )
            pin_input.send_keys(game_pin)

            enter_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enter')]")
            ))
            enter_button.click()

            username_input = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Nickname']"))
            )
            username_input.send_keys(username)

            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK, go!')]")
            ))
            ok_button.click()

            start_time = time.time()
            game_active = True  

            while game_active:
                elapsed_time = time.time() - start_time
                if elapsed_time >= 600:
                    print(f"Bot {username}: 10 minutes elapsed, staying in game...")

                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "nickname"))
                    )
                    print(f"Bot {username}: Still in game...")
                except:
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'All About')]")
                        ))
                        print(f"Bot {username}: Game over detected. Exiting...")
                        game_active = False
                    except:
                        print(f"Bot {username}: Possible disconnect, but still checking...")
                
                time.sleep(10)

            break

        except Exception as e:
            print(f"ERROR with bot {username} (Attempt {attempt}): {str(e)}")
            if attempt == max_retries:
                print(f"Bot {username}: Failed to join after {max_retries} attempts.")

        finally:
            print(f"Bot {username}: Closing browser...")
            driver.quit()
            if driver in drivers:
                drivers.remove(driver)

threads = []
for i in range(1, num_bots + 1):
    thread = threading.Thread(target=start_bot, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

close_all_browsers()
