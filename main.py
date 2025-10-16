import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

class FastGeminiAutomation:
    def __init__(self, edge_path):
        self.edge_path = edge_path
        self.driver = None
        self.wait = None
        self.last_response_count = 0
        
    def setup_driver(self):
        """Set up the Edge WebDriver"""
        edge_options = Options()
        edge_options.binary_location = self.edge_path
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        
        driver_path = self.get_driver_path()
        if not driver_path:
            print("Failed to set up Edge driver.")
            return False
            
        service = Service(driver_path)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.wait = WebDriverWait(self.driver, 15)
        return True
    
    def get_driver_path(self):
        """Get the Edge driver path"""
        possible_paths = [
            r"C:\Windows\System32\msedgedriver.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe",
            "./msedgedriver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Driver found: {path}")
                return path
        return None

    def open_gemini(self):
        """Open Google Gemini website"""
        print("Opening Google Gemini...")
        try:
            self.driver.get("https://gemini.google.com/")
            time.sleep(2)
            
            # Check if we need to login
            current_url = self.driver.current_url
            if "accounts.google.com" in current_url or "signin" in current_url:
                print("Please log in to your Google account in the browser window...")
                print("After logging in, press Enter in this terminal to continue.")
                input()
                self.driver.get("https://gemini.google.com/")
                time.sleep(2)
            else:
                print("Google Gemini loaded successfully!")
            
            return self.wait_for_gemini_ready()
            
        except Exception as e:
            print(f"Error opening Gemini: {e}")
            return False
    
    def wait_for_gemini_ready(self):
        """Wait for Gemini interface to be ready"""
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[contenteditable='true'], textarea, input")
            ))
            print("Gemini interface is ready!")
            return True
        except TimeoutException:
            print("Warning: Gemini interface took too long to load")
            return False
    
    def send_message(self, message):
        """Send a message to Gemini and wait for response"""
        try:
            # Find and use input element
            input_element = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[contenteditable='true']")
            ))
            
            # Clear and input message
            self.driver.execute_script("arguments[0].innerText = ''", input_element)
            input_element.click()
            input_element.send_keys(message)
            
            # Find and click send button
            send_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label*='Send']")
            ))
            send_button.click()
            
            print("Message sent. Waiting for response...")
            
            # Get response with optimized waiting
            response = self.wait_for_response_optimized()
            return response
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def wait_for_response_optimized(self):
        """Optimized waiting for Gemini response"""
        try:
            # Strategy 1: Wait for initial response to appear
            print("Waiting for response to appear...")
            
            # Count existing responses before we sent our message
            initial_responses = self.get_response_elements()
            
            # Wait for new response to start appearing
            start_time = time.time()
            last_text = ""
            stable_count = 0
            
            while time.time() - start_time < 45:  # Max 45 seconds
                current_responses = self.get_response_elements()
                
                # Check if we have a new response
                if len(current_responses) > len(initial_responses):
                    response_element = current_responses[-1]
                    current_text = response_element.text.strip()
                    
                    # If text is changing, it's still generating
                    if current_text != last_text:
                        last_text = current_text
                        stable_count = 0
                    else:
                        stable_count += 1
                    
                    # If text hasn't changed for 1.5 seconds, consider it complete
                    if stable_count >= 3 and len(current_text) > 10:
                        print("Response complete!")
                        return current_text
                
                time.sleep(0.5)  # Check every 500ms
            
            # Fallback: return whatever we have
            final_responses = self.get_response_elements()
            if len(final_responses) > len(initial_responses):
                return final_responses[-1].text.strip()
            
            return "Response timeout - no response received"
            
        except Exception as e:
            print(f"Error in response waiting: {e}")
            return self.get_fallback_response()
    
    def get_response_elements(self):
        """Get all response elements"""
        try:
            # Common selectors for Gemini responses
            selectors = [
                "[data-message-author-role='model']",
                "[class*='model-response']",
                "[class*='assistant-message']",
                ".message.model"
            ]
            
            all_responses = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    all_responses.extend(elements)
                except:
                    continue
            
            return all_responses
        except:
            return []
    
    def get_fallback_response(self):
        """Fallback method to get response"""
        try:
            # Get all text and find the latest substantial response
            body = self.driver.find_element(By.TAG_NAME, "body")
            lines = body.text.split('\n')
            
            # Filter out empty lines and short lines
            substantial_lines = [line.strip() for line in lines if len(line.strip()) > 20]
            
            if substantial_lines:
                # Return the last substantial line (likely the response)
                return substantial_lines[-1]
            
            return "Could not extract response"
        except:
            return "Error extracting response"
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed.")

def main():
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    if not os.path.exists(edge_path):
        print("Error: Microsoft Edge not found.")
        return
    
    gemini = FastGeminiAutomation(edge_path)
    
    try:
        print("Setting up Microsoft Edge...")
        if not gemini.setup_driver():
            return
        
        print("Opening Google Gemini...")
        if not gemini.open_gemini():
            return
        
        print("\n" + "="*50)
        print("FAST Gemini Terminal Interface")
        print("Type 'quit' to exit")
        print("="*50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                start_time = time.time()
                response = gemini.send_message(user_input)
                end_time = time.time()
                
                if response:
                    print(f"\nGemini ({end_time - start_time:.1f}s): {response}")
                else:
                    print("No response received")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        gemini.close()

if __name__ == "__main__":
    main()