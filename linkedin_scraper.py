from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_easy_apply_questions(driver, job_id):
    # Navigate to the job's detail page from search results
    driver.get(f"https://www.linkedin.com/jobs/view/{job_id}")

    # Wait for the page to load
    time.sleep(5)

    # This is a placeholder for the step to click the Easy Apply button.
    # The actual implementation may vary and requires identifying the button by its selector.
    # For demonstration purposes only:
    # easy_apply_button = driver.find_element(By.CLASS_NAME, "easy-apply-button")
    # easy_apply_button.click()
    
    # Wait for the Easy Apply form to load. Adjust timing based on network speed and response times.
    time.sleep(5)

    # Extract questions from the Easy Apply form
    # This assumes questions are labeled within the form. The actual implementation may need adjustments.
    questions_elements = driver.find_elements(By.CSS_SELECTOR, "label")
    questions = [element.text for element in questions_elements if element.text.strip() != ""]

    return questions
