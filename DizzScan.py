import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

def main():
    # Ask for the file containing URLs
    file_path = input("Enter the path to the file containing URLs (e.g., urls.txt): ")

    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist. Please check the path and try again.")
        return

    # Set up Selenium with a headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    # Create a directory to store screenshots
    output_dir = "screenshots"
    os.makedirs(output_dir, exist_ok=True)

    # Read URLs from the file and process each
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    for url in urls:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            print(f"Processing {url}...")
            driver.get(url)
            screenshot_path = os.path.join(output_dir, url.replace("http://", "").replace("https://", "").replace("/", "_") + ".png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
        except WebDriverException as e:
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                print(f"Failed to process {url}: DNS resolution failed (ERR_NAME_NOT_RESOLVED)")
            else:
                print(f"Failed to process {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")

    # Clean up
    driver.quit()
    print(f"All screenshots have been saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()
