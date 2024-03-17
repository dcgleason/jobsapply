import time
import math
import random
import os
import utils
import constants
import pickle
import hashlib
import yaml
import requests
import httpx
import json
import asyncio
import re
import traceback
import config
from typing import List
from utils import LinkedinUrlGenerate
from schemas import LinkedinConfig, LinkedinCredentials, ApplyDetails
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()



class Linkedin:
    def __init__(self, apply_details, userInfo):
        self.apply_details = apply_details
        self.config = apply_details.config
        self.credentials = apply_details.config.credentials
        self.userInfo = userInfo
        chrome_options = utils.chromeBrowserOptions(self.config)
        

           # Set the path to the ChromeDriver executable
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        
        if chromedriver_path:
             # Use the specified ChromeDriver path
            print(f"Using ChromeDriver from the specified path: {chromedriver_path}")
            self.driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
        #     self.driver.set_page_load_timeout(300)  # Increase the timeout to 5 minutes

        else:
            # Use ChromeDriverManager to automatically download and install ChromeDriver
         print("No chromedriver_path, using ChromeDriverManager to automatically download and install ChromeDriver")
         self.driver = webdriver.Chrome(chrome_options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
         self.driver.set_page_load_timeout(300)  # Increase the timeout to 5 minutes
       # running locally --> 
       # self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        
        # self.driver.get('https://www.google.com')
        # print(self.driver.page_source)

        utils.prYellow("🤖 Thanks for using BeyondNow Apply bot")
        utils.prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")

        #   # Set Chrome options
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--window-size=1920x1080")

       # self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

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
        email = self.credentials.linkedin_email
        password = self.credentials.linkedin_password.get_secret_value()

        try:
            self.driver.find_element(By.ID, "username").send_keys(email)
            self.driver.find_element(By.ID, "password").send_keys(password)
                # Submit the login form
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(15)  # Adjust timing as necessary
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
        time.sleep(10)
        job_links = []
        for i in range(num_jobs):
            job_link = self.driver.find_element(By.XPATH, f"(//a[contains(@href, '/jobs/view/')])[{i + 1}]")
            job_links.append(job_link.get_attribute('href'))
        return job_links
    

    # def scrape_easy_apply_questions(self, job_url):
    #     self.driver.get(job_url)
    #     WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")))
    #     easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
    #     easy_apply_button.click()

    #     questions_and_options = []

    #     def scrape_modal():
    #         # Wait for the modal to become visible
    #         WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".artdeco-modal__content")))
    #         time.sleep(5)  # Additional wait for all elements to load properly

    #         # Scrape all questions
    #         questions_elements = self.driver.find_elements(By.CSS_SELECTOR, "label")
    #         for element in questions_elements:
    #             question_text = element.text.strip()
    #             if question_text != "":
    #                 # Check if the question is a dropdown
    #                 parent = element.find_element(By.XPATH, "./..")
    #                 dropdown = parent.find_elements(By.CSS_SELECTOR, "select")
    #                 if dropdown:
    #                     # It's a dropdown, capture options
    #                     options = [opt.text for opt in dropdown[0].find_elements(By.TAG_NAME, "option")]
    #                     questions_and_options.append((question_text, options))
    #                 else:
    #                     # Not a dropdown, just a regular question
    #                     questions_and_options.append((question_text, None))

    #         # Check for "Next" button and click if present, else look for "Review" to end
    #         next_button = self.driver.find_elements(By.XPATH, "//button[contains(@data-control-name, 'continue')]")
    #         if next_button:
    #             next_button[0].click()
    #             scrape_modal()  # Recursively scrape the next modal
    #         else:
    #             review_button = self.driver.find_elements(By.XPATH, "//button[contains(@data-control-name, 'review')]")
    #             if review_button:
    #                 return  # Reached the review step, end recursion

    #         scrape_modal()
    #         return questions_and_options



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

    # def apply_to_job(self, job_url):
    #     # Navigate to the job's detail page
    #     self.driver.get(job_url)
    #     time.sleep(10)  # Wait for the page to load

    #     try:
    #         # Click the "Easy Apply" button
    #         easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]")
    #         easy_apply_button.click()
    #         time.sleep(5)  # Wait for the application form to load

    #         # TODO: Add steps to fill out the application form if necessary
    #         # Example:
    #         # self.driver.find_element(By.ID, 'form-field-id').send_keys('Your answer')

    #         # Submit the application
    #         submit_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
    #         submit_button.click()
    #         time.sleep(5)  # Wait for submission to complete

    #         print("Application submitted successfully.")
    #     except Exception as e:
    #         print(f"Failed to apply to job: {e}")


    # def fill_out_easy_apply_form(self, email, country_code, phone_number):
    #     # Wait for the modal to load
    #     time.sleep(5)

    #     # Select the email address
    #     email_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833898-multipleChoice")
    #     for option in email_dropdown.find_elements(By.TAG_NAME, 'option'):
    #         if option.text == email:
    #             option.click()
    #             break

    #     # Wait for the next elements to be interactable
    #     time.sleep(2)

    #     # Select the phone country code
    #     country_code_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833890-phoneNumber-country")
    #     for option in country_code_dropdown.find_elements(By.TAG_NAME, 'option'):
    #         if option.text == country_code:
    #             option.click()
    #             break

    #     # Wait for the next elements to be interactable
    #     time.sleep(2)

    #     # Enter the mobile phone number
    #     phone_number_field = self.driver.find_element(By.ID, "single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833890-phoneNumber-nationalNumber")
    #     phone_number_field.send_keys(phone_number)

    #     # Click the Next button to proceed to the next step of the application
    #     next_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step')]")
    #     next_button.click()

    #     # Add additional steps as needed based on the subsequent modals/forms

    # def select_first_resume_and_continue(self):
    #     # Wait for the modal content to load
    #     time.sleep(2)

    #     # Assuming the first resume is already selected by default based on your HTML snippet
    #     # If you need to select it explicitly, uncomment the following lines and adjust the selector as needed
    #     # first_resume = self.driver.find_element(By.CSS_SELECTOR, "input[type='radio'][id^='jobsDocumentCardToggle-']")
    #     # first_resume.click()
    #     # time.sleep(1)  # Wait for selection to be processed

    #     # Click the "Next" button to proceed
    #     next_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step')]")
    #     next_button.click()

    #     # Add additional steps as needed based on the subsequent modals/forms

    # def answer_citizenship_question_and_continue(self, is_us_citizen_or_gch):
    #     # Wait for the modal content to load
    #     time.sleep(4)

    #     # Find the dropdown for the citizenship question
    #     citizenship_dropdown = self.driver.find_element(By.ID, "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3826517437-112833874-multipleChoice")
        
    #     # Create a Select object for the dropdown
    #     select = Select(citizenship_dropdown)
        
    #     # Select the option based on the user's answer
    #     select.select_by_visible_text(is_us_citizen_or_gch)
    #     time.sleep(2)  # Wait for the selection to be processed

    #     # Click the "Review" button to proceed
    #     review_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Review your application')]")
    #     review_button.click()

    #     # Add additional steps as needed based on the subsequent modals/forms


    # def submit_job_application(self):
    #     # Wait for the page and the submit button to load
    #     time.sleep(2)  # Consider using WebDriverWait for better reliability

    #     # Locate the "Submit application" button by its aria-label attribute
    #     submit_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")

    #     # Click the "Submit application" button
    #     submit_button.click()

    #     # Optionally, add a wait or confirmation step here to ensure the application has been submitted successfully
    #     print("Application submitted.")

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
            
    async def wait_for_page_load_async(driver, timeout=10):
        await asyncio.sleep(30)
        page_title_contains_linkedin = False

        try:
            title = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//title[contains(text(), "LinkedIn")]'))
            )
            page_title_contains_linkedin = "LinkedIn" in title.get_attribute("textContent")
        except TimeoutException:
            print("Timed out waiting for the title element.")
        except AttributeError:
            print("'driver' object has no attribute 'title'")
            #print the page entire page source of url
            if driver.page_source is None:
                print(driver.current_url)
            else:
                print(driver.page_source)


        is_page_loaded = page_title_contains_linkedin
        if is_page_loaded:
            print("Page loaded successfully.")
            await asyncio.sleep(1)
            return True
        else:
            print("Page load timeout.")
            return False
        
    async def linkJobApply(self):
        logs = []

        url_generator = LinkedinUrlGenerate()
        job_urls = url_generator.generateUrlLinks(self.config)
        countJobs = 0
        print(f"Got job urls: {job_urls}")

        for url in job_urls:
            totalJobs = "0"
            self.driver.get(url)
            await asyncio.sleep(random.uniform(1, constants.botSpeed))
            print(f"Gotten to URL: {url}")

            if await self.wait_for_page_load_async(self.driver):
                try:
                    # WebDriverWait(self.driver, 10).until(
                    #     lambda driver: driver.execute_script("return document.readyState") == "complete"
                    # )
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//small'))
                    )
                    totalJobs = element.text
                    print(f"Total jobs: {totalJobs}")
                    totalPages = utils.jobsToPages(totalJobs)

                    urlWords = utils.urlToKeywords(url)
                    lineToWrite = "\n Category: " + urlWords[0] + ", Location: " + urlWords[1] + ", Applying " + str(totalJobs) + " jobs."
                    log_message = self.displayWriteResults(lineToWrite)
                    logs.append(log_message)

                except:
                    print(f"Error: Element not found.")
                    print(f"URL: {self.driver.current_url}")
                    try:
                        relevant_html = self.driver.execute_script("""
                            var element = document.evaluate("//div[@class='jobs-search-results-list__title-heading']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (element) {
                                var outerHTML = element.outerHTML;
                                return outerHTML;
                            } else {
                                return "Element not found";
                            }
                        """)
                        print("Relevant HTML:")
                        print(relevant_html)
                    except Exception as script_error:
                        print(f"Error executing JavaScript: {str(script_error)}")
                    totalJobs = "0"
            else:
                print(f"Error: Page load timeout!!")
                totalJobs = "0"

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                pageUrl = url + "&start=" + str(currentPageJobs)
                self.driver.get(pageUrl)
                print(f"Accessing page URL: {pageUrl}")
                await asyncio.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [offer.get_attribute("data-occludable-job-id").split(":")[-1] for offer in offersPerPage]
                await asyncio.sleep(random.uniform(1, constants.botSpeed))

                for offerId in offerIds:
                    offerPage = f'https://www.linkedin.com/jobs/view/{offerId}'
                    self.driver.get(offerPage)
                    await asyncio.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1
                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties:
                        lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " + str(offerPage)
                        log_message = self.displayWriteResults(lineToWrite)
                        logs.append(log_message)
                    else:
                        easyApplyButton = self.easyApplyButton()

                        if easyApplyButton is not False:
                            easyApplyButton.click()
                            print(f"Clicked easy apply button on {offerPage}")
                            await asyncio.sleep(random.uniform(1, constants.botSpeed))

                            while True:
                                modalbox_open = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                                )
                                modal_type = self.get_modal_type()
                                print(f"Modal type identified: {modal_type} on {offerPage}")

                                if modal_type == "select_and_string":
                                    await self.fill_all_string_inputs()
                                    await self.fill_all_select_inputs()
                                    next_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Continue to next step']")
                                    review_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Review your application']")
                                    submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
                                    if next_button:
                                        await self.wait_and_click("//button[@aria-label='Continue to next step']")
                                    elif review_button:
                                        await self.wait_and_click("//button[@aria-label='Review your application']")
                                    elif submit_button:
                                        await self.wait_and_click("//button[@aria-label='Submit application']")
                                        lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                        log_message = self.displayWriteResults(lineToWrite)
                                        logs.append(log_message)
                                        break
                                    else:
                                        break
                                elif modal_type == "choose_resume":
                                    await self.chooseResume()
                                    next_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Continue to next step']")
                                    review_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Review your application']")
                                    submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
                                    if next_button:
                                        await self.wait_and_click("//button[@aria-label='Continue to next step']")
                                    elif review_button:
                                        await self.wait_and_click("//button[@aria-label='Review your application']")
                                    elif submit_button:
                                        await self.wait_and_click("//button[@aria-label='Submit application']")
                                        lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                        log_message = self.displayWriteResults(lineToWrite)
                                        logs.append(log_message)
                                        break
                                    else:
                                        break
                                elif modal_type == "radio_buttons":
                                    await self.fill_all_radio_buttons()
                                    next_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Continue to next step']")
                                    review_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Review your application']")
                                    submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
                                    if next_button:
                                        await self.wait_and_click("//button[@aria-label='Continue to next step']")
                                    elif review_button:
                                        await self.wait_and_click("//button[@aria-label='Review your application']")
                                    elif submit_button:
                                        await self.wait_and_click("//button[@aria-label='Submit application']")
                                        lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                        log_message = self.displayWriteResults(lineToWrite)
                                        logs.append(log_message)
                                        break
                                    else:
                                        break
                                elif modal_type == "radio_and_string":
                                    await self.fill_all_radio_buttons()
                                    next_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Continue to next step']")
                                    review_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Review your application']")
                                    submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
                                    if next_button:
                                        await self.wait_and_click("//button[@aria-label='Continue to next step']")
                                    elif review_button:
                                        await self.wait_and_click("//button[@aria-label='Review your application']")
                                    elif submit_button:
                                        await self.wait_and_click("//button[@aria-label='Submit application']")
                                        lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                        log_message = self.displayWriteResults(lineToWrite)
                                        logs.append(log_message)
                                        break
                                    else:
                                        break
                                elif modal_type == "submit":
                                    submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
                                    await self.wait_and_click("//button[@aria-label='Submit application']")
                                    lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: " + str(offerPage)
                                    log_message = self.displayWriteResults(lineToWrite)
                                    logs.append(log_message)
                                    break
                                else:
                                    break
                        else:
                            lineToWrite = jobProperties + " | " + f"* 🥵 Cannot apply to this Job! {str(offerPage)}"
                            log_message = self.displayWriteResults(lineToWrite)
                            logs.append(log_message)

        return logs

  
        
    async def answer_additional_questions(self, **user_details):
        additional_questions = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form-element')]")
        all_questions_answered = True

        for question in additional_questions:
            question_type = self.determine_question_type(question)
            question_label = self.extract_question_label(question)

            if question_type == "input":
                input_field = question.find_element(By.TAG_NAME, "input")
                answer = await self.ask_gpt4(question_label, "string", user_details)
                input_field.send_keys(answer)
            elif question_type == "select":
                select_element = question.find_element(By.TAG_NAME, "select")
                options = [option.get_attribute("value") for option in select_element.find_elements(By.TAG_NAME, "option")]
                options = [opt for opt in options if opt.lower() != "select an option"]
                answer = await self.ask_gpt4(question_label, "choice", options, user_details)
                Select(select_element).select_by_value(answer)
            elif question_type == "radio":
                radio_buttons = question.find_elements(By.XPATH, ".//input[@type='radio']")
                answer_index = int(await self.ask_gpt4(question_label, "choice", user_details)) - 1
                if 0 <= answer_index < len(radio_buttons):
                    radio_buttons[answer_index].click()
                else:
                    all_questions_answered = False
            else:
                all_questions_answered = False

            await asyncio.sleep(random.uniform(1, constants.botSpeed))

        return all_questions_answered
    
    def get_modal_type(self):
        select_and_string = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form-element')]//input") or \
                            self.driver.find_elements(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form-element')]//select")
        choose_resume = self.driver.find_elements(By.CLASS_NAME, "jobs-document-upload__title--is-required")
        radio_buttons = self.driver.find_elements(By.XPATH, "//fieldset[contains(@data-test-form-builder-radio-button-form-component, 'true')]")
        review_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Review your application']")
        submit_button = self.driver.find_elements(By.XPATH, "//button[@aria-label='Submit application']")
        select_string_resume_submit = select_and_string and choose_resume and submit_button
        radio_and_string = radio_buttons and select_and_string

        if select_string_resume_submit:
            print("select_string_resume_submit")
            return "select_string_resume_submit"
        elif radio_and_string:
            print("radio_and_string")
            return "radio_and_string"
        elif select_and_string:
            print("select_and_string")
            return "select_and_string"
        elif choose_resume:
            print("choose_resume")
            return "choose_resume"
        elif radio_buttons:
            print("radio_buttons")
            return "radio_buttons"
        elif review_button:
            print("review_button")
            return "review"
        elif submit_button:
            print("submit_button")
            return "submit"
        else:
            return "unknown"
            

    async def fill_all_radio_buttons(self):
        print("Filling all radio buttons")
        radio_button_fieldsets = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//fieldset[contains(@data-test-form-builder-radio-button-form-component, 'true')]"))
        )
        for fieldset in radio_button_fieldsets:
            question_text = WebDriverWait(fieldset, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//legend/span"))
            ).text.strip()
            print(f"Question: {question_text}")
            radio_button_labels = WebDriverWait(fieldset, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//label"))
            )
            options = [label.text.strip() for label in radio_button_labels]
            
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                answer = await self.ask_gpt4(question_text, "choice", options=options)
                print(f"GPT-4 Answer: {answer}")  # Print the received answer
                
                try:
                    if answer in options:
                        answer_label = next(label for label in radio_button_labels if label.text.strip() == answer)
                        answer_label.click()
                        break
                    else:
                        print(f"Invalid answer received from GPT-4: {answer}")
                        retry_count += 1
                except Exception as e:
                    print(f"Error while clicking radio button label: {str(e)}")
                    retry_count += 1
            
            if retry_count == max_retries:
                print(f"Failed to select a valid radio button after {max_retries} retries.")
        
        await asyncio.sleep(random.uniform(1, constants.botSpeed))

    def determine_question_type(self, question):
        if question.find_elements(By.TAG_NAME, "input"):
            return "input"
        elif question.find_elements(By.TAG_NAME, "select"):
            return "select"
        elif question.find_elements(By.XPATH, ".//input[@type='radio']"):
            return "radio"
        else:
            return "unknown"

    def extract_question_label(self, question):
        label_element = question.find_element(By.XPATH, ".//label")
        return label_element.text if label_element else "Unknown Question"

    async def ask_gpt4(self, question, question_type, options=None):
        prompt = f"Statement: {question}\nType: {question_type}\n"

        if question_type == "string":
            prompt += "Please provide a concise and relevant answer to the statement based on the user's information.\n"
        elif question_type == "choice":
            if options:
                options_text = "Options:\n" + "\n".join([f"{opt}" for opt in options]) + "\n"
                prompt += options_text
                prompt += "Please select the option that best fits the given statement by providing the exact option text. The response should only contain the selected option text, without any additional characters or explanations. If none of the options are suitable, respond with 'None'.\n"
            else:
                raise ValueError("Options must be provided for question type 'choice'.")
        else:
            raise ValueError(f"Unsupported question type: {question_type}")

        prompt = f"{self.userInfo}\n\n{prompt}\nAnswer:"  # Include userInfo in the prompt

        print(f"Generated Prompt:\n{prompt}\n")  # Print the generated prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://127.0.0.1:8000/ask-gpt4/",
                json={"question": prompt, "question_type": question_type, "options": options, "userInfo": self.userInfo}  # Include userInfo in the request payload
            )

        if response.status_code == 200:
            answer_data = response.json()
            answer = answer_data["answers"]
            print(f"GPT-4 Answer: {answer}\n")  # Print the received answer
            return answer
        else:
            raise Exception(f"Failed to get response from GPT-4 for question '{question}': {response.text}")
        
    async def wait_and_click(self, xpath):
        """Wait for an element to be clickable and click it."""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            await asyncio.sleep(random.uniform(1, constants.botSpeed))
        except TimeoutException:
            print(f"Element with xpath {xpath} not clickable.")

    # async def apply_to_job(self, job_url, resume_path, phone_number):
    #     self.driver.get(job_url)
    #     apply_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Easy Apply"]')
    #     apply_button.click()
        
    #     await self.upload_resume(resume_path)
    #     await self.fill_contact_info(phone_number)
        
    #     next_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Continue to next step"]')
    #     next_button.click()
        
    #     # Handling additional questions dynamically
    #     await self.handle_additional_questions()

    #     submit_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Submit application"]')
    #     submit_button.click()

   
    # async def ask_gpt4(questions: list, question_type: str = "string", options: list = None):
    #     answers = []
    #     async with httpx.AsyncClient() as client:
    #         for question in questions:
    #             response = await client.post(
    #                 'http://127.0.0.1:8000/ask-gpt4/',
    #                 json={"question": question, "question_type": question_type, "options": options}
    #             )
    #             if response.status_code == 200:
    #                 answer_data = response.json()
    #                 answers.append(answer_data['answers'])
    #             else:
    #                 raise Exception(f"Failed to get response from GPT-4 for question '{question}': {response.text}")
    #     return answers
            
    async def fill_all_string_inputs(self):
        # Find all parent divs
        parent_divs = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        for parent_div in parent_divs:
            # Check if the div has an input element
            input_fields = parent_div.find_elements(By.TAG_NAME, 'input')
            for input_field in input_fields:
                # Find the label for the input field within the parent div
                try:
                    label = parent_div.find_element(By.XPATH, './/label').text
                except Exception as e:
                    label = "Please provide input"  # Default prompt if no label is found

                max_retries = 3
                retry_count = 0
                error = False
                while retry_count < max_retries:
                    # Use ask_gpt4 to generate an answer for the label/question

                    if error == False:

                        answers = await self.ask_gpt4([label], "string")
                        answer = answers  # Extract the first (and only) answer and remove leading/trailing whitespace

                        # Clear the input field before sending keys
                        input_field.clear()
                        # Send the generated answer to the input field
                        input_field.send_keys(answer)
                        # Wait for a random time between 1 and 3 seconds
                        await asyncio.sleep(random.uniform(1, 3))

                    # Check for inline error messages
                    error_message_elements = parent_div.find_elements(By.XPATH, ".//span[contains(@class, 'artdeco-inline-feedback__message')]")
                    if error_message_elements:
                        error_message = error_message_elements[0].text
                        print(f"Error encountered: {error_message}")
                        error = True
                        # Send the error message to GPT-4 for generating a new response
                        answers = await self.ask_gpt4([f"Error: {error_message}. Please provide a valid input for: {label}"], "string")
                        answer = answers
                        input_field.clear()
                        # Send the generated answer to the input field
                        input_field.send_keys(answer)

                        retry_count += 1
                    else:
                        break

                if retry_count == max_retries:
                    print(f"Failed to fill input field after {max_retries} retries.")

    async def fill_all_select_inputs(self):
        # Find all parent divs
        parent_divs = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        for parent_div in parent_divs:
            # Check if the div has a select element
            select_elements = parent_div.find_elements(By.TAG_NAME, 'select')
            for select_element in select_elements:
                # Find the label for the select element within the parent div
                try:
                    label = parent_div.find_element(By.XPATH, './/label').text
                except NoSuchElementException:
                    label = "Please select an option"  # Default prompt if no label is found

                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    # Extract options from the select element
                    options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]
                    # Remove placeholder if necessary
                    options = [opt for opt in options if opt.lower() != "select an option"]

                    # Use ask_gpt4 to generate an answer for the label/question with options
                    selected_options = await self.ask_gpt4([label], "choice", options=options)
                    selected_option = selected_options # Extract the first (and only) selected option and remove leading/trailing whitespace

                    if selected_option.lower() == 'none':
                        Select(select_element).select_by_index(0)
                        print(f"Warning: GPT-4 responded with 'None' for the question '{label}'. Selecting the first option as a fallback.")
                    else:
                        try:
                            Select(select_element).select_by_visible_text(selected_option)
                        except NoSuchElementException:
                            # If the selected option is not found, try selecting by value
                            try:
                                Select(select_element).select_by_value(selected_option)
                            except NoSuchElementException:
                                Select(select_element).select_by_index(0)
                                print(f"Warning: Selected option '{selected_option}' not found for the question '{label}'. Selecting the first option as a fallback.")

                    # Wait for a random time between 1 and 3 seconds
                    await asyncio.sleep(random.uniform(1, 3))

                    # Check for inline error messages
                    error_message_elements = parent_div.find_elements(By.XPATH, ".//span[contains(@class, 'artdeco-inline-feedback__message')]")
                    if error_message_elements:
                        error_message = error_message_elements[0].text
                        print(f"Error encountered: {error_message}")
                        # Send the error message to GPT-4 for generating a new response
                        selected_options = await self.ask_gpt4([f"Error: {error_message}. Please select a valid option for: {label}"], "choice", options=options)
                        selected_option = selected_options
                        retry_count += 1
                    else:
                        break

                if retry_count == max_retries:
                    print(f"Failed to fill select field after {max_retries} retries.")

    # original code
    # async def fill_all_string_inputs(self):
    #     # Find all parent divs
    #     parent_divs = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-element')
    #     for parent_div in parent_divs:
    #         # Check if the div has an input element
    #         input_fields = parent_div.find_elements(By.TAG_NAME, 'input')
    #         for input_field in input_fields:
    #             # Find the label for the input field within the parent div
    #             try:
    #                 label = parent_div.find_element(By.XPATH, './/label').text
    #             except Exception as e:
    #                 label = "Please provide input"  # Default prompt if no label is found

    #             # Use ask_gpt4 to generate an answer for the label/question
    #             answers = await self.ask_gpt4([label], "string")
    #             answer = answers  # Extract the first (and only) answer and remove leading/trailing whitespace

    #             # Clear the input field before sending keys
    #             input_field.clear()
    #             # Send the generated answer to the input field
    #             input_field.send_keys(answer)
    #             # Wait for a random time between 1 and 3 seconds
    #             await asyncio.sleep(random.uniform(1, 3))

    # async def fill_all_select_inputs(self):
    #     # Find all parent divs
    #     parent_divs = self.driver.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-element')
    #     for parent_div in parent_divs:
    #         # Check if the div has a select element
    #         select_elements = parent_div.find_elements(By.TAG_NAME, 'select')
    #         for select_element in select_elements:
    #             # Find the label for the select element within the parent div
    #             try:
    #                 label = parent_div.find_element(By.XPATH, './/label').text
    #             except NoSuchElementException:
    #                 label = "Please select an option"  # Default prompt if no label is found

    #             # Extract options from the select element
    #             options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]
    #             # Remove placeholder if necessary
    #             options = [opt for opt in options if opt.lower() != "select an option"]

    #             # Use ask_gpt4 to generate an answer for the label/question with options
    #             selected_options = await self.ask_gpt4([label], "choice", options=options)
    #             selected_option = selected_options[0].strip()  # Extract the first (and only) selected option and remove leading/trailing whitespace

    #             if selected_option.lower() == 'none':
    #                 Select(select_element).select_by_index(0)
    #                 print(f"Warning: GPT-4 responded with 'None' for the question '{label}'. Selecting the first option as a fallback.")
    #             else:
    #                 try:
    #                     # Try to select the option by visible text first
    #                     Select(select_element).select_by_visible_text(selected_option)
    #                 except NoSuchElementException:
    #                     # If the exact text doesn't match, try to find the option that contains the response
    #                     options = select_element.find_elements(By.TAG_NAME, 'option')
    #                     selected = False
    #                     for option in options:
    #                         if selected_option in option.text:
    #                             option.click()
    #                             selected = True
    #                             break
    #                     if not selected:
    #                         # If no matching option is found, select the first option as a fallback
    #                         Select(select_element).select_by_index(0)
    #                         print(f"Warning: No matching option found for '{selected_option}' in the question '{label}'. Selecting the first option as a fallback.")

    #             # Wait for a random time between 1 and 3 seconds
    #             await asyncio.sleep(random.uniform(1, 3))
            
    # async def handle_additional_questions(self):
    #     # Assuming all additional questions are text input fields
    #     text_input_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
    #     for field in text_input_fields:
    #         field.send_keys('Answer')  # Replace 'Answer' with the actual answer or dynamic logic to generate the answer
    #         await asyncio.sleep(random.uniform(0.5, 1.5))

    # def handleApplicationQuestions(self):
    #     # Check for different types of input fields
    #     self.handleTextInputFields()
    #     self.handleSelectDropdowns()
    #     self.handleRadioButtons()

    #     # Assuming there might be a "Next" button to navigate through modal pages
    #     next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
    #     for next_button in next_buttons:
    #         try:
    #             if next_button.is_displayed() and next_button.is_enabled():
    #                 next_button.click()
    #                 time.sleep(random.uniform(1, constants.botSpeed))
    #                 self.handleApplicationQuestions()  # Recursively handle questions on the next page
    #         except Exception as e:
    #             print(f"Error navigating modal pages: {e}")

    # async def handleTextInputFields(self):
    #     text_input_elements = self.driver.find_elements(By.XPATH, "//input[@type='text']")
    #     for element in text_input_elements:
    #         try:
    #             # Traverse up to the common parent and then find the label within that scope
    #             parent_container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element')]")
    #             label = parent_container.find_element(By.XPATH, ".//label")
    #             question_text = label.text if label else "Default Question"
                
    #             # Assuming ask_gpt4 is an async function. If not, you'll need to adjust this part.
    #             answer = await self.ask_gpt4(question_text)
    #             element.send_keys(answer)
    #         except Exception as e:
    #             print(f"Failed to process text input field: {e}")

    # async def handleSelectDropdowns(self):
    #     # Find all select elements and their corresponding labels for questions
    #     select_elements = self.driver.find_elements(By.XPATH, "//select[contains(@data-test-text-entity-list-form-select, '')]")
    #     for select_element in select_elements:
    #         # Find the label associated with the select element
    #         # Assuming the label is a direct preceding sibling of the select's parent div
    #         label = select_element.find_element(By.XPATH, "./preceding-sibling::label")
    #         question_text = label.text.strip() if label else "Default Question"
            
    #         # Extract options from the select element
    #         options = [option.text.strip() for option in Select(select_element).options if option.text.strip() != "Select an option"]
            
    #         # Assuming ask_gpt4 is a synchronous function that returns the answer as a string
    #         # If it's asynchronous, you'll need to adjust the call accordingly
    #         answer = await self.ask_gpt4(question_text, options)
            
    #         # Select the option that matches the answer returned by GPT-4
    #         try:
    #             Select(select_element).select_by_visible_text(answer)
    #         except Exception as e:
    #             print(f"Error selecting option: {e}")

    def find_corresponding_label(self, element):
        # Implement logic to find the label corresponding to an input/select element
        label_for = element.get_attribute("id")
        return self.driver.find_element(By.XPATH, f"//label[@for='{label_for}']")

    # async def handleRadioButtons(self):
    #     fieldsets = self.driver.find_elements(By.XPATH, "//fieldset[contains(@data-test-form-builder-radio-button-form-component, 'true')]")
    #     for fieldset in fieldsets:
    #         try:
    #             question_text = fieldset.find_element(By.XPATH, ".//legend/span").text.strip()
    #             # Use await to get the answer asynchronously
    #             answer_index = int(await self.ask_gpt4(question_text)) - 1
                
    #             radio_buttons = fieldset.find_elements(By.XPATH, ".//input[@type='radio']")
    #             if 0 <= answer_index < len(radio_buttons):
    #                 radio_buttons[answer_index].click()
    #             else:
    #                 print(f"Invalid answer index received from GPT-4: {answer_index}")
    #         except NoSuchElementException:
    #             print("Question text or radio button not found.")
    #         except Exception as e:
    #             print(f"Error handling radio buttons: {str(e)}")
                



    # async def handle_modals_in_sequence(self):
    #     # Interact with the first modal
    #     await self.fill_out_contact_info()
    #     # Click the "Next" button on the first modal
    #     await self.wait_and_click("//button[contains(text(), 'Next')]")

    #     # Interact with the second modal (e.g., uploading a resume)
    #     await self.select_first_resume_and_continue()
    #     # Click the "Next" button on the second modal
    #     await self.wait_and_click("//button[contains(text(), 'Next')]")

    #     # Interact with the third modal (e.g., answering additional questions)
    #     await self.answer_additional_questions()
    #     # Click the "Review" button on the third modal
    #     await self.wait_and_click("//button[contains(text(), 'Review')]")

    #     # Interact with the fourth modal (e.g., final review)
    #     await self.final_review()
    #     # Click the "Submit application" button on the fourth modal
    #     await self.wait_and_click("//button[contains(text(), 'Submit application')]")

    # def process_job_page(self):
    #     """Process the current job page."""
    #     page_text = self.extract_text_from_page()
    #     questions = self.detect_questions(page_text)
    #     answers = self.ask_gpt4(questions)
    #     for question, answer in zip(questions, answers):
    #         print(f"Q: {question}\nA: {answer}\n")

    # def chooseResume(self):
    #     try:
    #         self.driver.find_element(
    #             By.CLASS_NAME, "jobs-document-upload__title--is-required")
    #         resumes = self.driver.find_elements(
    #             By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
    #         if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
    #             resumes[0].click()
    #         elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
    #             resumes[config.preferredCv-1].click()
    #         elif (type(len(resumes)) != int):
    #             utils.prRed(
    #                 "❌ No resume has been selected please add at least one resume to your Linkedin account.")
    #     except:
    #         pass

    def is_choose_resume_modal(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "jobs-document-upload__title--is-required")
            return True
        except:
            return False

    async def chooseResume(self):
        try:
            resumes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if resumes:
                selected_resume = None
                for resume in resumes:
                    if resume.get_attribute("aria-label") == "Selected":
                        selected_resume = resume
                        break

                if not selected_resume:
                    if len(resumes) == 1:
                        resumes[0].click()
                    elif len(resumes) > 1:
                        resumes[1 - 1].click()
            else:
                utils.prRed("❌ No resume has been selected. Please add at least one resume to your LinkedIn account.")
        except Exception as e:
            utils.prRed(f"❌ Error while choosing resume: {str(e)}")
            
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
            return lineToWrite

        except Exception as e:
            utils.prRed("❌ Error in DisplayWriteResults: " +str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0

# start = time.time()
# Linkedin().linkJobApply()
# end = time.time()
# utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
