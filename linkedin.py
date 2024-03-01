import time
import math
import random
import os
import utils
import constants
import config
import pickle
import hashlib
import yaml
import requests
from typing import List
from utils import LinkedinUrlGenerate
from schemas import LinkedinConfig, LinkedinCredentials, ApplyDetails




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select




options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional: if you want to run Chrome in headless mode
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


class Linkedin:
    def __init__(self, apply_details):
        self.apply_details = apply_details
        self.config = apply_details.config
        self.credentials = self.config.credentials  # Extracting credentials from the config

        utils.prYellow("🤖 Thanks for using BeyondNow Apply bot")
        utils.prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")

        # Set Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        cookies_dir = os.path.join(os.getcwd(), 'cookies')
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)

        self.cookies_path = f"{cookies_dir}/{self.getHash(self.credentials.linkedin_email)}.pkl"

        self.driver.get('https://www.linkedin.com')
        self.loadCookies()

        if not self.isLoggedIn():
            self.login()

    def login(self):
        self.driver.get("https://www.linkedin.com/login")
            # Accessing credentials from the dynamic configuration
        email = self.apply_details.config.credentials.linkedin_email
        password = self.apply_details.config.credentials.linkedin_password

        try:
            self.driver.find_element(By.ID, "username").send_keys(email)
            self.driver.find_element(By.ID, "password").send_keys(password)
                # Submit the login form
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(5)  # Adjust timing as necessary
        except Exception as e:
            utils.prRed(f"❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials. Error: {str(e)}")
        self.saveCookies()


    def getHash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)



    def get_job_links(self, search_query, num_jobs=10):
        self.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={search_query}")
        time.sleep(5)
        job_links = []
        for i in range(num_jobs):
            job_link = self.driver.find_element(By.XPATH, f"(//a[contains(@href, '/jobs/view/')])[{i + 1}]")
            job_links.append(job_link.get_attribute('href'))
        return job_links
    

    def scrape_easy_apply_questions(self, job_url):
        self.driver.get(job_url)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")))
        easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
        easy_apply_button.click()

        questions_and_options = []

        def scrape_modal():
            # Wait for the modal to become visible
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".artdeco-modal__content")))
            time.sleep(2)  # Additional wait for all elements to load properly

            # Scrape all questions
            questions_elements = self.driver.find_elements(By.CSS_SELECTOR, "label")
            for element in questions_elements:
                question_text = element.text.strip()
                if question_text != "":
                    # Check if the question is a dropdown
                    parent = element.find_element(By.XPATH, "./..")
                    dropdown = parent.find_elements(By.CSS_SELECTOR, "select")
                    if dropdown:
                        # It's a dropdown, capture options
                        options = [opt.text for opt in dropdown[0].find_elements(By.TAG_NAME, "option")]
                        questions_and_options.append((question_text, options))
                    else:
                        # Not a dropdown, just a regular question
                        questions_and_options.append((question_text, None))

            # Check for "Next" button and click if present, else look for "Review" to end
            next_button = self.driver.find_elements(By.XPATH, "//button[contains(@data-control-name, 'continue')]")
            if next_button:
                next_button[0].click()
                scrape_modal()  # Recursively scrape the next modal
            else:
                review_button = self.driver.find_elements(By.XPATH, "//button[contains(@data-control-name, 'review')]")
                if review_button:
                    return  # Reached the review step, end recursion

            scrape_modal()
            return questions_and_options



    def saveCookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def isLoggedIn(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember14"]')
            return True
        except:
            pass
        return False
    
    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                url_generator = LinkedinUrlGenerate()
                linkedinJobLinks = url_generator.generateUrlLinks(self.config)  # Pass self.config here
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            utils.prGreen("✅ Apply urls are created successfully, now the bot will visit those urls.")
        except Exception as e:
            utils.prRed(f"❌ Couldn't generate urls, make sure you have edited config file line 25-39. Error: {str(e)}")

    # def linkJobApplyTwo(self, max_jobs_to_apply=10):
    #     # Navigate to the job search page (assuming the URL is already set)
    #     # self.driver.get("Your LinkedIn job search URL")
    #     time.sleep(5)  # Wait for the page to load

    #     # Find all job listing elements
    #     job_listings = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
    #     applied_count = 0

    #     for job_listing in job_listings:
    #         if applied_count >= max_jobs_to_apply:
    #             break

    #         # Extract the job link
    #         try:
    #             job_link_element = job_listing.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
    #             job_link = job_link_element.get_attribute('href')
    #             print(f"Applying to: {job_link}")

    #             # Call the apply_to_job method with the job link
    #             self.apply_to_job(job_link)

    #             applied_count += 1
    #             print(f"Successfully applied to {applied_count} jobs")
    #         except Exception as e:
    #             print(f"Could not apply to job: {e}")
    #         finally:
    #             # Go back to the job listings page to continue the loop if necessary
    #             # This might be optional depending on whether the apply_to_job method navigates away from the job page
    #             # self.driver.get("Your LinkedIn job search URL")
    #             time.sleep(2)

    #     print(f"Finished applying to {applied_count} jobs")

    def apply_to_job(self, job_url):
        # Navigate to the job's detail page
        self.driver.get(job_url)
        time.sleep(5)  # Wait for the page to load

        try:
            # Click the "Easy Apply" button
            easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]")
            easy_apply_button.click()
            time.sleep(2)  # Wait for the application form to load

            # TODO: Add steps to fill out the application form if necessary
            # Example:
            # self.driver.find_element(By.ID, 'form-field-id').send_keys('Your answer')

            # Submit the application
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
            submit_button.click()
            time.sleep(2)  # Wait for submission to complete

            print("Application submitted successfully.")
        except Exception as e:
            print(f"Failed to apply to job: {e}")


    def fill_out_easy_apply_form(self, email, country_code, phone_number):
        # Wait for the modal to load
        time.sleep(2)

        # Select the email address
        email_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833898-multipleChoice")
        for option in email_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == email:
                option.click()
                break

        # Wait for the next elements to be interactable
        time.sleep(1)

        # Select the phone country code
        country_code_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833890-phoneNumber-country")
        for option in country_code_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == country_code:
                option.click()
                break

        # Wait for the next elements to be interactable
        time.sleep(1)

        # Enter the mobile phone number
        phone_number_field = self.driver.find_element(By.ID, "single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833890-phoneNumber-nationalNumber")
        phone_number_field.send_keys(phone_number)

        # Click the Next button to proceed to the next step of the application
        next_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step')]")
        next_button.click()

        # Add additional steps as needed based on the subsequent modals/forms

    def select_first_resume_and_continue(self):
        # Wait for the modal content to load
        time.sleep(2)

        # Assuming the first resume is already selected by default based on your HTML snippet
        # If you need to select it explicitly, uncomment the following lines and adjust the selector as needed
        # first_resume = self.driver.find_element(By.CSS_SELECTOR, "input[type='radio'][id^='jobsDocumentCardToggle-']")
        # first_resume.click()
        # time.sleep(1)  # Wait for selection to be processed

        # Click the "Next" button to proceed
        next_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step')]")
        next_button.click()

        # Add additional steps as needed based on the subsequent modals/forms

    def answer_citizenship_question_and_continue(self, is_us_citizen_or_gch):
        # Wait for the modal content to load
        time.sleep(2)

        # Find the dropdown for the citizenship question
        citizenship_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833874-multipleChoice")
        
        # Create a Select object for the dropdown
        select = Select(citizenship_dropdown)
        
        # Select the option based on the user's answer
        select.select_by_visible_text(is_us_citizen_or_gch)
        time.sleep(1)  # Wait for the selection to be processed

        # Click the "Review" button to proceed
        review_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Review your application')]")
        review_button.click()

        # Add additional steps as needed based on the subsequent modals/forms


    def submit_job_application(self):
        # Wait for the page and the submit button to load
        time.sleep(2)  # Consider using WebDriverWait for better reliability

        # Locate the "Submit application" button by its aria-label attribute
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")

        # Click the "Submit application" button
        submit_button.click()

        # Optionally, add a wait or confirmation step here to ensure the application has been submitted successfully
        print("Application submitted.")

    # def linkJobApply(self):
    #     self.generateUrls()
    #     countApplied = 0
    #     countJobs = 0

    #     urlData = utils.getUrlDataFile()

    #     for url in urlData:        
    #         self.driver.get(url)
    #         time.sleep(random.uniform(1, constants.botSpeed))

    #         totalJobs = self.driver.find_element(By.XPATH,'//small').text 
    #         totalPages = utils.jobsToPages(totalJobs)

    #         urlWords =  utils.urlToKeywords(url)
    #         lineToWrite = "\n Category: " + urlWords[0] + ", Location: " +urlWords[1] + ", Applying " +str(totalJobs)+ " jobs."
    #         self.displayWriteResults(lineToWrite)

    #         for page in range(totalPages):
    #             currentPageJobs = constants.jobsPerPage * page
    #             url = url +"&start="+ str(currentPageJobs)
    #             self.driver.get(url)
    #             time.sleep(random.uniform(1, constants.botSpeed))

    #             offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
    #             offerIds = [(offer.get_attribute(
    #                 "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
    #             time.sleep(random.uniform(1, constants.botSpeed))

    #             for offer in offersPerPage:
    #                 if not self.element_exists(offer, By.XPATH, ".//*[contains(text(), 'Applied')]"):
    #                     offerId = offer.get_attribute("data-occludable-job-id")
    #                     offerIds.append(int(offerId.split(":")[-1]))

    #             for jobID in offerIds:
    #                 offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
    #                 self.driver.get(offerPage)
    #                 time.sleep(random.uniform(1, constants.botSpeed))

    #                 countJobs += 1

    #                 jobProperties = self.getJobProperties(countJobs)
    #                 if "blacklisted" in jobProperties: 
    #                     lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " +str(offerPage)
    #                     self.displayWriteResults(lineToWrite)
                    
    #                 else :                    
    #                     easyApplybutton = self.easyApplyButton()

    #                     if easyApplybutton is not False:
    #                         easyApplybutton.click()
    #                         time.sleep(random.uniform(1, constants.botSpeed))
                            
    #                         try:
    #                             self.chooseResume()
    #                             self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
    #                             time.sleep(random.uniform(1, constants.botSpeed))

    #                             lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: "  +str(offerPage)
    #                             self.displayWriteResults(lineToWrite)
    #                             countApplied += 1

    #                         except:
    #                             try:
    #                                 self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
    #                                 time.sleep(random.uniform(1, constants.botSpeed))
    #                                 self.chooseResume()
    #                                 comPercentage = self.driver.find_element(By.XPATH,'html/body/div[3]/div/div/div[2]/div/div/span').text
    #                                 percenNumber = int(comPercentage[0:comPercentage.index("%")])
    #                                 result = self.applyProcess(percenNumber,offerPage)
    #                                 lineToWrite = jobProperties + " | " + result
    #                                 self.displayWriteResults(lineToWrite)
                                
    #                             except Exception: 
    #                                 self.chooseResume()
    #                                 lineToWrite = jobProperties + " | " + "* 🥵 Cannot apply to this Job! " +str(offerPage)
    #                                 self.displayWriteResults(lineToWrite)
    #                     else:
    #                         lineToWrite = jobProperties + " | " + "* 🥳 Already applied! Job: " +str(offerPage)
    #                         self.displayWriteResults(lineToWrite)


    #         utils.prYellow("Category: " + urlWords[0] + "," +urlWords[1]+ " applied: " + str(countApplied) +
    #               " jobs out of " + str(countJobs) + ".")
        
    #     utils.donate(self)

    def linkJobApply(self):
        
        # self.generateUrls()
        countApplied = 0
        countJobs = 0
        url_generator = LinkedinUrlGenerate()
        job_urls = url_generator.generateUrlLinks(self.config)

        urlData = utils.getUrlDataFile()

        for url in urlData:        
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH, '//small').text 
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + urlWords[0] + ", Location: " + urlWords[1] + ", Applying " + str(totalJobs) + " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                pageUrl = url + "&start=" + str(currentPageJobs)
                self.driver.get(pageUrl)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [offer.get_attribute("data-occludable-job-id").split(":")[-1] for offer in offersPerPage]
                time.sleep(random.uniform(1, constants.botSpeed))

                for offerId in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(offerId)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1
                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties:
                        lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " + str(offerPage)
                        self.displayWriteResults(lineToWrite)
                    else:
                        easyApplybutton = self.easyApplyButton()

                        if easyApplybutton is not False:
                            easyApplybutton.click()
                            time.sleep(random.uniform(1, constants.botSpeed))
                            
                            try:
                                self.chooseResume()
                                # Handling the job application questions more dynamically
                                self.handleApplicationQuestions()

                                # Submit the application
                                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
                                if submit_button:
                                    submit_button.click()
                                    time.sleep(random.uniform(1, constants.botSpeed))
                                    lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                                    countApplied += 1
                                else:
                                    raise Exception("Submit button not found")
                            except Exception as e:
                                lineToWrite = jobProperties + " | " + f"* 🥵 Cannot apply to this Job! {str(offerPage)} Exception: {str(e)}"
                                self.displayWriteResults(lineToWrite)

    def handleApplicationQuestions(self):
        # Check for different types of input fields
        self.handleTextInputFields()
        self.handleSelectDropdowns()
        self.handleRadioButtons()

        # Assuming there might be a "Next" button to navigate through modal pages
        next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
        for next_button in next_buttons:
            try:
                if next_button.is_displayed() and next_button.is_enabled():
                    next_button.click()
                    time.sleep(random.uniform(1, constants.botSpeed))
                    self.handleApplicationQuestions()  # Recursively handle questions on the next page
            except Exception as e:
                print(f"Error navigating modal pages: {e}")

    def handleTextInputFields(self):
        text_input_elements = self.driver.find_elements(By.XPATH, "//input[@type='text']")
        for element in text_input_elements:
            # Attempt to find the parent container of the input element
            parent_container = element.find_element(By.XPATH, "./..")
            # Within this container, try to locate the label element that contains the question
            label = parent_container.find_element(By.TAG_NAME, "label")
            question_text = label.text if label else "Default Question"
            
            answer = self.ask_gpt4(question_text)
            element.send_keys(answer)

    def handleSelectDropdowns(self):
        # Find all select elements and their corresponding labels for questions
        select_elements = self.driver.find_elements(By.TAG_NAME, "select")
        for element in select_elements:
            label = self.find_corresponding_label(element)
            question_text = label.text
            options = [option.text for option in Select(element).options]
            answer = self.ask_gpt4(question_text, options)
            Select(element).select_by_visible_text(answer)

    def find_corresponding_label(self, element):
        # Implement logic to find the label corresponding to an input/select element
        label_for = element.get_attribute("id")
        return self.driver.find_element(By.XPATH, f"//label[@for='{label_for}']")

    def handleRadioButtons(self):
        # This method needs to be more dynamic to handle various questions and radio button options
        fieldsets = self.driver.find_elements(By.XPATH, "//fieldset[contains(@data-test-form-builder-radio-button-form-component, 'true')]")
        for fieldset in fieldsets:
            try:
                legend = fieldset.find_element(By.TAG_NAME, 'legend').text
                if not legend:
                    # Attempt to get the question from associated label if legend is not directly available
                    legend = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, ".//legend/span"))).text
                answer = self.ask_gpt4(legend)
                # Logic to decide which radio button to click based on the answer from GPT-4
                # This is a simplified example. You'll need to adjust this logic based on the expected answers from GPT-4
                if "yes" in answer.lower():
                    yes_button = fieldset.find_element(By.XPATH, ".//input[@type='radio' and @value='Yes']")
                    yes_button.click()
                elif "no" in answer.lower():
                    no_button = fieldset.find_element(By.XPATH, ".//input[@type='radio' and @value='No']")
                    no_button.click()
            except NoSuchElementException:
                print("Radio button or question not found.")
            except TimeoutException:
                print("Timeout waiting for radio button question.")

    def ask_gpt4(self, question: str, question_type: str = "string", options: list = None):
            """
            Send a question to GPT-4 and get an answer, dynamically handling the question type.
            
            Args:
                question (str): The question to be answered by GPT-4.
                question_type (str): The type of the question (e.g., "string", "select", "radio").
                options (list): Options for the question, applicable for "select" or "radio" types.
            
            Returns:
                The answer from GPT-4, formatted according to the question type.
            """
            # Define the FastAPI endpoint URL
            fastapi_endpoint = 'http://127.0.0.1:8000/ask-gpt4/'
            # Prepare the JSON payload for the request
            payload = {
                "question": question,
                "question_type": question_type,
                "options": options
            }
            # Make the POST request to the FastAPI endpoint
            response = requests.post(fastapi_endpoint, json=payload)
            if response.status_code == 200:
                # Process the response based on the question type
                answer = response.json()['answers']
                if question_type in ["select", "radio"] and options:
                    # Convert answer index back to the option text if necessary
                    try:
                        # Assuming the answer is an index for select/radio types
                        answer_idx = int(answer) - 1
                        return options[answer_idx]
                    except (ValueError, IndexError):
                        raise Exception(f"Invalid answer index returned by GPT-4: {answer}")
                return answer
            else:
                raise Exception(f"Failed to get a response from GPT-4: {response.text}")



    def process_job_page(self):
        """Process the current job page."""
        page_text = self.extract_text_from_page()
        questions = self.detect_questions(page_text)
        answers = self.ask_gpt4(questions)
        for question, answer in zip(questions, answers):
            print(f"Q: {question}\nA: {answer}\n")

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                resumes[0].click()
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                resumes[config.preferredCv-1].click()
            elif (type(len(resumes)) != int):
                utils.prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account.")
        except:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                utils.prYellow("⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(5)
            jobDetail = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow("⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow("⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle +" | " + jobDetail + jobLocation
        return textToWrite

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.XPATH, "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]")
            EasyApplyButton = button
        except: 
            EasyApplyButton = False

        return EasyApplyButton

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2 
        result = ""
        for pages in range(applyPages):  
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()

        self.driver.find_element( By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        if config.followCompanies is False:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
            except:
                pass

        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "* 🥳 Just Applied to this job: " + str(offerPage)

        return result

    def displayWriteResults(self,lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            utils.prRed("❌ Error in DisplayWriteResults: " +str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0

# start = time.time()
# Linkedin().linkJobApply()
# end = time.time()
# utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
