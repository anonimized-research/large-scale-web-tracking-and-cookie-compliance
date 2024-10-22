from bs4 import BeautifulSoup
import re
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
import random

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep
from bs4 import BeautifulSoup
import shutil
from pathlib import Path

def remove_curly_braces(text):
    # Define a regular expression pattern to find text within curly braces
    pattern = r'\{.*\}'
    
    # Use re.sub() to replace all occurrences of the pattern with an empty string
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text

def is_page_fully_loaded(driver):
    # Execute JavaScript to check if the document is ready
    return driver.execute_script("return document.readyState") == "complete"

def wait_for_consistent_load(driver, num_checks=6, interval=0.1):
    # This function makes sure that there are no asynchronous or pending loads that still haven't begun
    load_counts = 0
    for _ in range(num_checks):
        if is_page_fully_loaded(driver):
            load_counts += 1
            
        time.sleep(interval)
    
    return load_counts == num_checks
            
def end_scroll(driver):
    body = driver.find_element("tag name", "body")
    
    # Simulate pressing and holding the END key
    driver.execute_script("""
        var event = new KeyboardEvent('keydown', {
            key: 'End',
            code: 'End',
            charCode: 35,
            keyCode: 35,
            which: 35
        });
        document.dispatchEvent(event);
    """)
    time.sleep(random.uniform(0.05, 0.1))  # Hold the key down for X seconds

    # Simulate releasing the END key
    driver.execute_script("""
        var event = new KeyboardEvent('keyup', {
            key: 'End',
            code: 'End',
            charCode: 35,
            keyCode: 35,
            which: 35
        });
        document.dispatchEvent(event);
    """)

def append_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text)

def extract_text_from_url(url, uuid_str, error_file, chromedriver_path, max_retries=1, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode (without opening browser window)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--crash-dumps-dir=/tmp") 
            chrome_options.add_argument("--shm-size=2g")
            chrome_options.add_argument("--disable-extensions")

            # Specify unique directories for each instance (use process ID, UUID, etc.)
            unique_profile = Path(f'/tmp/chrome_profile_{uuid_str}')
            unique_profile.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(f'/tmp/chrome_profile_{uuid_str}')

            chrome_options.add_argument(f"--user-data-dir={unique_profile}")
            
            # Initialize the UserAgent object
            ua = UserAgent()
            # Get a random User-Agent
            user_agent = ua.random
            chrome_options.add_argument(f'user-agent={user_agent}')

            path = chromedriver_path

            chrome_service = Service(executable_path=path)
            
            # Create the WebDriver and set the browser options
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            print(" - Webdriver started")

            # Connect to Chrome DevTools Protocol (CDP)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Set custom headers
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'DNT': '1',  # Do Not Track Request Header
                'Referer': 'https://www.google.com/',
                'Upgrade-Insecure-Requests': '1',
            }

            # Intercept network requests to add headers
            def interceptor(request):
                for key, value in headers.items():
                    request.headers[key] = value
                request.continue_()

            driver.request_interceptor = interceptor
            # Set window size to allow size dependent elements to be loaded
            # Also set large height to force all the webpage to load
            driver.set_window_size(1920, 17500)
            ##### Techniques to avoid bot detection
            # Report a more common resolution
            driver.execute_script("Object.defineProperty(screen, 'width', {get: function () { return 1920; }});")
            driver.execute_script("Object.defineProperty(screen, 'height', {get: function () { return 1080; }});")
            # Change the language
            driver.execute_script("Object.defineProperty(navigator, 'language', {get: function () { return 'en-US'; },});")
            
            # Change the platform and webdriver
            driver.execute_script("Object.defineProperty(navigator, 'platform', {get: function () { return 'Win32'; },});")
            
            #####
            # Navigate to the URL
            # Changing the property of the navigator value for webdriver to undefined 
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            # Set the page load timeout
            driver.set_page_load_timeout(10) # Considered a timeout if it takes more than 10s
            driver.get(url)
            
            # Scroll to the bottom of the page
            end_scroll(driver)
            # Wait until the page is fully loaded
            WebDriverWait(driver, 10).until(wait_for_consistent_load)

            print(" - Website fully loaded")
            
            # Find the body element
            body = driver.find_element("tag name", "body")
            
            # Execute JavaScript to hide all fixed and sticky elements, and dialogs or popups, that contain certain keywords (among other elements)
            driver.execute_script("""

                function traverseNodes(node, elements) {
                    var allElements = node.querySelectorAll('*');
                    for (var i = 0; i < allElements.length; i++) {
                        elements.push(allElements[i]);
                    }
                
                    // Check for shadow roots and traverse into them
                    var shadowRoots = node.querySelectorAll('*');
                    shadowRoots.forEach(function(shadowRoot) {
                        var shadowTree = shadowRoot.shadowRoot;
                        if (shadowTree) {
                            traverseNodes(shadowTree, elements);
                        }
                    });
                }


                            
                var elements = []; //document.body.getElementsByTagName('*');
                traverseNodes(document.body, elements); 
                var items = []; 
                var words = ['policy', 'cooki', 'políti', 'galet', 'gallet', 'accept', 'consent', 'uc-'];
                var ariaAttributes = ['aria-describedby', 'sr-only'];
                for (var i = 0; i < elements.length; i++) {
                    var element = elements[i];
                    var attributes = element.attributes;
                    var computedStyle = window.getComputedStyle(element);
                    
                    var hasAriaAttribute = ariaAttributes.some(attr => element.hasAttribute(attr) || element.className && element.className.toString().includes(attr)) ;
                    var attributeContainsDialogOrPopup = attributes && Array.from(attributes).some(attr => attr.value.includes('dialog') || attr.value.includes('popup'));
                    
                    //"Invisible" Text
                    if(computedStyle.getPropertyValue('height') === '1px' || computedStyle.getPropertyValue('width') === '1px'){
                        items.push(element);
                    }
                    //Cookie Banners
                    else if ((getComputedStyle(element).position === 'fixed' || getComputedStyle(element).position === 'sticky'
                    || element.getAttribute('role') === "dialog"/*|| attributeContainsDialogOrPopup*/) && 
                        words.some(word => element.innerText && element.innerText.includes(word))) {
                        items.push(element);
                    }
                    else if (words.some(word => (element.className && element.className.toString().includes(word) || element.tagName && element.tagName.includes(word)
                    )) &&
                    words.some(word => element.innerText && element.innerText.includes(word))) {
                        items.push(element);
                    }
                    else if(element.className && element.className.toString().includes('addoor')){
                        items.push(element);
                    }
                    else if (element.getAttribute('role') === "dialog") {
                        items.push(element);
                    }
                }

                for (var i = 0; i < items.length; i++) {
                   if (items[i].parentNode) {  // Check if parentNode exists
                       items[i].parentNode.removeChild(items[i]);
                   }
                }
            """)
            # Extract text content using Selenium
            text = driver.find_element(By.TAG_NAME, 'body').text
            # Remove curly braces
            text = remove_curly_braces(text)
            
            # Check if the number of words is less than 250
            if len(text.split()) < 250:
                # If the fetched text is too short, we'll add the text from a less sophisticated approach
                # In some cases, this will be much more useful
                
                # Get the page source HTML
                html = driver.page_source

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the body element and get its text
                soup_text = soup.body.get_text()
            
                # Append the new text to the existing text
                text += " " + soup_text

                print(" - BeautifulSoup used")
            
            return text
        
        except Exception as e:
            if e is None:
                append_to_file(error_file, 'E\n')
            else:
                append_to_file(error_file, 'E\n')
                append_to_file(error_file, str(e))
                print()
            print(f"Error occurred while fetching the URL: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
        finally:
            try:
                # Close the WebDriver
                if driver:
                    driver.quit()
            except UnboundLocalError:
                pass

    print("Maximum number of retries reached. Unable to fetch the URL:", url)
    return None
