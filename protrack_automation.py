import os
import time
import glob
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

def rename_latest_pdf(download_dir, report_name, start_date, end_date):
    """Rename the latest PDF file with proper naming convention"""
    start_fmt = datetime.strptime(start_date, "%m/%d/%Y").strftime("%m%d%y")
    end_fmt = datetime.strptime(end_date, "%m/%d/%Y").strftime("%m%d%y")
    date_str = f"{start_fmt}to{end_fmt}"

    pdf_files = glob.glob(os.path.join(download_dir, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in the download folder.")
        return

    latest_file = max(pdf_files, key=os.path.getctime)
    clean_name = report_name.replace("/", "-").replace("\\", "-")
    new_filename = f"{clean_name} {date_str}.pdf"
    new_path = os.path.join(download_dir, new_filename)

    shutil.move(latest_file, new_path)
    print(f"Renamed PDF to: {new_filename}")

def rename_latest_excel(download_dir, report_name, start_date, end_date):
    """Rename the latest Excel file with proper naming convention"""
    start_fmt = datetime.strptime(start_date, "%m/%d/%Y").strftime("%m%d%y")
    end_fmt = datetime.strptime(end_date, "%m/%d/%Y").strftime("%m%d%y")
    date_str = f"{start_fmt}to{end_fmt}"

    excel_files = glob.glob(os.path.join(download_dir, "*.xlsx"))
    if not excel_files:
        print("No Excel files found in the download folder.")
        return

    latest_file = max(excel_files, key=os.path.getctime)
    clean_name = report_name.replace("/", "-").replace("\\", "-")
    new_filename = f"{clean_name} {date_str}.xlsx"
    new_path = os.path.join(download_dir, new_filename)

    shutil.move(latest_file, new_path)
    print(f"Renamed Excel to: {new_filename}")

def run_automation(username, password, start_date, end_date):
    """Main automation function that can be called from the web interface"""
    
    # Download directory
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Reports to process
    reports_to_process = [
        "2031 Employee Performance",
        "2031 Employee Ranking",
        "2031 Performance",
        "2041 Employee Performance",
        "2041 Employee Ranking",
        "2041 Performance",
        "2050 Employee Performance",
        "2050 Employee Ranking",
        "2050 Performance",
        "2131 Employee Performance",
        "2131 Employee Ranking",
        "2131 Performance",
        "Fabiola Garcia Employee Performance",
        "Fabiola Garcia Employee Ranking",
        "Fabiola Garcia Performance",
        "Jesse Dodge Employee Performance",
        "Jesse Dodge Employee Ranking",
        "Jesse Dodge Performance",
        "June Gibson Winward Employee Performance",
        "June Gibson Winward Employee Ranking",
        "June Gibson Winward Performance",
        "June Gibson Yummie Employee Performance",
        "June Gibson Yummie Employee Ranking",
        "June Gibson Yummie Performance",
        "KUIU Employee Performance",
        "KUIU Employee Ranking",
        "KUIU Performance",
        "Laura Gallagher Employee Performance",
        "Laura Gallagher Employee Ranking",
        "Laura Gallagher Performance",
        "Maria Solis Employee Performance",
        "Maria Solis Employee Ranking",
        "Maria Solis Performance",
        "McDonough Employee Performance",
        "McDonough Employee Ranking",
        "McDonough Performance",
        "Rasim Sumovic Employee Performance",
        "Rasim Sumovic Employee Ranking",
        "Rasim Sumovic Performance",
        "Remy de Leon Employee Performance",
        "Remy de Leon Employee Ranking",
        "Remy de Leon Performance",
    ]

    # Chrome setup
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # Remove headless mode for better compatibility
    # options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"Failed to initialize Chrome driver: {e}")
        print("Trying with system Chrome driver...")
        driver = webdriver.Chrome(options=options)

    try:
        print("Opening ProTrack website...")
        driver.get("https://nb.protrackwarehouse.com/")
        driver.execute_script("document.body.style.zoom='100%'")
        
        print("Waiting for login page to load...")
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        print("Entering credentials...")
        username_field.clear()
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        print("Clicking login button...")
        login_button = driver.find_element(By.ID, "kc-login")
        login_button.click()
        
        print("Waiting for dashboard to load...")
        # Wait for successful login by checking for Reports link
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Reports"))
        )
        print("Login successful!")

        print("Navigating to Reports...")
        reports_link = driver.find_element(By.LINK_TEXT, "Reports")
        reports_link.click()
        
        print("Navigating to Ad Hoc Reporting...")
        adhoc_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Ad Hoc Reporting"))
        )
        adhoc_link.click()

        print("Refreshing page to ensure full load...")
        driver.refresh()
        
        print("Waiting for Ad Hoc Reporting page to fully load...")
        profile_dropdown = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "profileName"))
        )
        
        print("Waiting for dropdown to be populated...")
        retries = 10
        for i in range(retries):
            try:
                listbox_loaded = driver.execute_script("""
                    const list = document.querySelector('#profileName_listbox');
                    return list && list.children && list.children.length > 0;
                """)
                if listbox_loaded:
                    print("Dropdown list is populated and ready.")
                    break
                else:
                    print(f"Waiting for dropdown to populate... ({i+1}/{retries})")
                    time.sleep(3)
            except Exception as e:
                print(f"Error checking dropdown: {e}")
                time.sleep(3)
        else:
            print("Warning: Dropdown might not be fully populated, but continuing...")
            
        # Additional wait to ensure page is stable
        time.sleep(5)

        total_reports = len(reports_to_process)
        for i, report in enumerate(reports_to_process, 1):
            print(f"Processing report {i}/{total_reports}: {report}")
            
            try:
                # Click dropdown to open it
                dropdown_trigger = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@aria-controls='profileName_listbox']"))
                )
                dropdown_trigger.click()
                time.sleep(1)

                # Find and clear search input
                search_input = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@name='profileName_input']"))
                )
                search_input.clear()
                search_input.send_keys(report)
                time.sleep(2)

                # Select the report from dropdown
                try:
                    report_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//ul[@id='profileName_listbox']/li[contains(text(), '{report}')]"))
                    )
                    report_option.click()
                    time.sleep(1)
                except Exception as e:
                    print(f"Could not find report '{report}' in dropdown: {e}")
                    continue

                # Set start date
                from_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'From')]/following-sibling::td//input"))
                )
                from_input.clear()
                from_input.send_keys(start_date)
                from_input.send_keys(Keys.TAB)
                time.sleep(1)

                # Set end date
                to_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'To')]/following-sibling::td//input"))
                )
                to_input.clear()
                to_input.send_keys(end_date)
                to_input.send_keys(Keys.TAB)
                time.sleep(1)

                print("Submitting report request...")
                main_window = driver.current_window_handle
                submit_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='btnSave' and @value='Submit']"))
                )
                submit_button.click()

                # Wait for new window to open
                print("Waiting for report window to open...")
                WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
                
                # Switch to new window
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)

                # Wait for report to load
                print("Waiting for report data to load...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "k-grid-content"))
                )
                time.sleep(3)

                # Export to PDF
                print("Exporting to PDF...")
                try:
                    pdf_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.k-button.k-button-icontext.k-grid-pdf"))
                    )
                    pdf_button.click()
                    print("PDF export initiated, waiting for download...")
                    time.sleep(12)
                    rename_latest_pdf(download_dir, report, start_date, end_date)
                except Exception as e:
                    print(f"PDF export failed for {report}: {e}")

                # Export to Excel
                print("Exporting to Excel...")
                try:
                    excel_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.k-button.k-button-icontext.k-grid-excel"))
                    )
                    excel_button.click()
                    print("Excel export initiated, waiting for download...")
                    time.sleep(12)
                    rename_latest_excel(download_dir, report, start_date, end_date)
                except Exception as e:
                    print(f"Excel export failed for {report}: {e}")

                # Close report window and return to main window
                driver.close()
                driver.switch_to.window(main_window)
                
                # Progress update
                progress = (i / total_reports) * 100
                print(f"Progress: {progress:.1f}% ({i}/{total_reports} reports completed)")
                
            except Exception as e:
                print(f"Error processing report '{report}': {e}")
                # Try to return to main window if we're in a different window
                try:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(main_window)
                except:
                    pass
                continue

    except Exception as e:
        print(f"Script failed: {str(e)}")
        raise e

    finally:
        driver.quit()
        print("Browser closed. Automation completed!")

if __name__ == "__main__":
    # For testing purposes - this won't run when imported
    print("This script should be run through the web interface")
    print("Start the web server with: python app.py")