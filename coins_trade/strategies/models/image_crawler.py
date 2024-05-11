import time
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By



def fetch_images_from_google(search_query, num_images):
    # Path to ChromeDriver
    
    # Setting up WebDriver

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Prepare the query URL
    query = '+'.join(search_query.split())
    url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    
    # Load the page
    driver.get(url)
    print("Scrolling page...")
    # Scroll to the end of the page to load all images
    for _ in range(500):
        print(f"Range: {_}")
        driver.execute_script("window.scrollBy(0,1000000)")
        time.sleep(0.5)
    
    # Find image elements
    images = driver.find_element(By.CSS_SELECTOR('img.rg_i'))
    count = 0
    print(images)
    # Directory to save images
    import os
    directory = os.path.join(os.getcwd(), search_query)
    print(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Download images
    for image in images:
        if count >= num_images:
            break
        try:
            # Click on each image to retrieve the high resolution version
            image.click()
            time.sleep(0.5)  # let the high-res image load
            high_res_images = driver.find_elements_by_css_selector('img.n3VNCb')
            for high_res_image in high_res_images:
                url = high_res_image.get_attribute('src')
                if url and 'http' in url:
                    # Save the image
                    response = requests.get(url)
                    img = Image.open(BytesIO(response.content))
                    img.save(os.path.join(directory, f'{count}.png'))
                    count += 1
                    break
        except Exception as e:
            print(f"Failed to download image: {e}")
    
    driver.quit()

# Usage
fetch_images_from_google('Falling Wedge pattern trading', 30)
