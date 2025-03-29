import os
import logging
import threading
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Configure logging
logging.basicConfig(filename='dizzscan.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

def process_url(url, driver, output_dir):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        logging.info(f"Processing {url}...")
        driver.get(url)
        screenshot_path = os.path.join(output_dir, url.replace("http://", "").replace("https://", "").replace("/", "_") + ".png")
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved: {screenshot_path}")
        # Check for security headers
        check_security_headers(driver, url)
    except WebDriverException as e:
        if "ERR_NAME_NOT_RESOLVED" in str(e):
            logging.error(f"Failed to process {url}: DNS resolution failed (ERR_NAME_NOT_RESOLVED)")
        else:
            logging.error(f"Failed to process {url}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing {url}: {e}")

def check_security_headers(driver, url):
    headers = driver.execute_script("return Object.fromEntries(new Headers([...document.cookie.split('; ').map(cookie => cookie.split('=')).map(([k, v]) => [k, decodeURIComponent(v)])]))")
    missing_headers = []
    required_headers = [
        'Content-Security-Policy',
        'Strict-Transport-Security',
        'X-Content-Type-Options'
    ]
    for header in required_headers:
        if header not in headers:
            missing_headers.append(header)
    if missing_headers:
        logging.warning(f"Missing security headers for {url}: {', '.join(missing_headers)}")
    else:
        logging.info(f"All security headers are present for {url}")

def main():
    parser = argparse.ArgumentParser(description='Capture screenshots and check for security headers.')
    parser.add_argument('file_path', help='Path to the file containing URLs (e.g., urls.txt)')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to use (default: 4)')
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"File '{args.file_path}' does not exist. Please check the path and try again.")
        return

    # Set up Selenium with a headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)

    # Create a directory to store screenshots
    output_dir = "screenshots"
    os.makedirs(output_dir, exist_ok=True)

    # Read URLs from the file and process each
    with open(args.file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    # Use threading to process URLs concurrently
    threads = []
    for url in urls:
        if len(threads) >= args.threads:
            for thread in threads:
                thread.join()
            threads = []
        thread = threading.Thread(target=process_url, args=(url, driver, output_dir))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Clean up
    driver.quit()
    print(f"All screenshots have been saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()
