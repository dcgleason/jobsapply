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


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional: if you want to run Chrome in headless mode
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


class Linkedin:
    def __init__(self, additional_questions_path='additionalQuestions.yaml'):
        utils.prYellow("🤖 Thanks for using BeyondNow Apply bot")
        utils.prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")

        # Load additional questions
        self.additional_questions = self.load_additional_questions(additional_questions_path)

        # Set Chrome options for headless execution
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--window-size=1920x1080")  # Specify window size

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        # Ensure the cookies directory exists
        cookies_dir = os.path.join(os.getcwd(), 'cookies')
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)

        self.cookies_path = f"{cookies_dir}/{self.getHash(config.email)}.pkl"

        self.driver.get('https://www.linkedin.com')
        self.loadCookies()

        if not self.isLoggedIn():
            self.login()
        # Start application
        self.linkJobApply()

    def load_additional_questions(self, file_path):
        """Load additional questions from a YAML file."""
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def login(self):
        self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        utils.prYellow("🔄 Trying to log in Linkedin...")
        try:
            self.driver.find_element("id", "username").send_keys(config.email)
            time.sleep(2)
            self.driver.find_element("id", "password").send_keys(config.password)
            time.sleep(2)
            self.driver.find_element("xpath", '//button[@type="submit"]').click()
            time.sleep(30)
        except:
            utils.prRed("❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")
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
            with open('data/urlData.txt', 'w',encoding="utf-8" ) as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url+ "\n")
            utils.prGreen("✅ Apply urls are created successfully, now the bot will visit those urls.")
        except:
            utils.prRed("❌ Couldn't generate urls, make sure you have editted config file line 25-39")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:        
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH,'//small').text 
            totalPages = utils.jobsToPages(totalJobs)

            urlWords =  utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + urlWords[0] + ", Location: " +urlWords[1] + ", Applying " +str(totalJobs)+ " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url +"&start="+ str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [(offer.get_attribute(
                    "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
                time.sleep(random.uniform(1, constants.botSpeed))

                for offer in offersPerPage:
                    if not self.element_exists(offer, By.XPATH, ".//*[contains(text(), 'Applied')]"):
                        offerId = offer.get_attribute("data-occludable-job-id")
                        offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1

                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties: 
                        lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " +str(offerPage)
                        self.displayWriteResults(lineToWrite)
                    
                    else :                    
                        easyApplybutton = self.easyApplyButton()

                        if easyApplybutton is not False:
                            easyApplybutton.click()
                            time.sleep(random.uniform(1, constants.botSpeed))
                            
                            try:
                                self.chooseResume()
                                self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                                time.sleep(random.uniform(1, constants.botSpeed))

                                lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: "  +str(offerPage)
                                self.displayWriteResults(lineToWrite)
                                countApplied += 1

                            except:
                                try:
                                    self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']").click()
                                    time.sleep(random.uniform(1, constants.botSpeed))
                                    self.chooseResume()
                                    comPercentage = self.driver.find_element(By.XPATH,'html/body/div[3]/div/div/div[2]/div/div/span').text
                                    percenNumber = int(comPercentage[0:comPercentage.index("%")])
                                    result = self.applyProcess(percenNumber,offerPage)
                                    lineToWrite = jobProperties + " | " + result
                                    self.displayWriteResults(lineToWrite)
                                
                                except Exception: 
                                    self.chooseResume()
                                    lineToWrite = jobProperties + " | " + "* 🥵 Cannot apply to this Job! " +str(offerPage)
                                    self.displayWriteResults(lineToWrite)
                        else:
                            lineToWrite = jobProperties + " | " + "* 🥳 Already applied! Job: " +str(offerPage)
                            self.displayWriteResults(lineToWrite)


            utils.prYellow("Category: " + urlWords[0] + "," +urlWords[1]+ " applied: " + str(countApplied) +
                  " jobs out of " + str(countJobs) + ".")
        
        utils.donate(self)

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

start = time.time()
Linkedin().linkJobApply()
end = time.time()
utils.prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
