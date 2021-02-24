import logging, time, os
from typing import Counter
from threading import Thread
from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from .miscellaneous import is_connected, connectionCheck, LOCK, bbPermissionFlag, logger,threeFailedInputs,fiveFailedAttempts



class LoginBB():
    """
        This cell handels logging into Black Board (BB)

        Attributes:
            userName: UID of student.
            password: password of student.
            chromePath: path to default chrome profile
    """



    def __init__(self, userName, password, chromePath,browserName):
        self.userName = userName
        self.password = password
        self.chromePath = chromePath
        self.browserName = browserName



    # logging into BB account
    def loginBB(self):

        if self.browserName == "Google Chrome":
            # declaring webdriver
            try:
                chrome_options = chromeOptions()
                chrome_options.add_argument("--use-fake-ui-for-media-stream")
                chrome_options.add_argument('log-level=3')
                chrome_options.add_argument("--start-maximized")
                driver = webdriver.Chrome(options=chrome_options)
            except:
                logger.error("Check if chromedrivers are in the path")
                input()
                exit()


        elif self.browserName == "Brave":
            BraveFlag=False
            try:
                brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                brave_options = chromeOptions()
                brave_options.add_argument("--use-fake-ui-for-media-stream")
                brave_options.add_argument('log-level=3')
                brave_options.add_argument("--start-maximized")
                brave_options.binary_location = brave_path
                driver = webdriver.Chrome(chrome_options=brave_options)
                BraveFlag=True
            except:
                logger.error("Check if chromedrivers are in the path")


            if not BraveFlag:
                try:
                    brave_path = "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                    brave_options = chromeOptions()
                    brave_options.add_argument("--use-fake-ui-for-media-stream")
                    brave_options.add_argument('log-level=3')
                    brave_options.add_argument("--start-maximized")
                    brave_options.binary_location = brave_path
                    driver = webdriver.Chrome(chrome_options=brave_options)
                except:
                    logger.error("Check if chromedrivers are in the path")
                    logger.warning("Exiting ..... ")
                    input()
                    exit()


        elif self.browserName == "Mozilla Firefox":
            try:
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--use-fake-ui-for-media-stream")
                firefox_options.add_argument('log-level=3')
                firefox_options.add_argument("--start-maximized")
                driver = webdriver.Firefox(options=firefox_options)
            except:
                logger.error("Check if geeckodriver are in the path")
                input()
                exit()


        networkAvaliable = connectionCheck()
        if not networkAvaliable:
            is_connected()
        

        # entering username and password in BB
        counter=0
        while(networkAvaliable):
            counter+=1

            try:
                driver.get('https://cuchd.blackboard.com/')
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='button-1']"))).click()
                driver.find_element_by_name('user_id').send_keys(self.userName)
                driver.find_element_by_name('password').send_keys(self.password)
                driver.find_element_by_id('entry-login').click()
                break
            except:
                logger.error("Unable to login BB")
                is_connected()

            if counter==5:
                fiveFailedAttempts()


        time.sleep(2)
        driver.get("https://cuchd.blackboard.com/ultra/course")
        currentURL = str(driver.current_url)


        if currentURL == "https://cuchd.blackboard.com/ultra/course":
            logger.info("Logged in successfully to Black Board")

        return driver



class ClassManagement():
    def __init__(self):
        pass


    def fromWhichLecture(self,allDetails):
        # asking user from which lecture he/she wants to join
        # keeps on asking till the right input is given
        counter = 0
        while(True):
            # if int input is given or not
            counter+=1
            try:
                lectureNumber = int(input("Enter from which Lecture you want to Attend: "))
                print()
                # if wrong input is given
                if((lectureNumber>len(allDetails)) or (lectureNumber<=0)):
                    logger.warning("There are only " + str(len(allDetails)) + " Lectures Today")
                else:
                    break
            except:
                logger.error("Invalid Input!!")
                logger.info("Input can only be a number.")

            if counter==3:
                threeFailedInputs()

        return lectureNumber


    # substracting 15 minutes from class joining time
    def joinClassDetails(self,data):
        time12H = datetime.strptime(f"{data[0]}", "%I:%M %p")
        classAttendTime = time12H - timedelta(minutes=15)

        return classAttendTime



    # adding 45 minutes to class joining time
    def nextClassDetails(self,data):
        time12H = datetime.strptime(f"{data[0]}", "%I:%M %p")
        classAttendTime = time12H + timedelta(minutes=45)

        return classAttendTime



    # comparing current and class join time
    def compareTime(self,classJoinTime):
        currentTime = datetime.now()
        classEndTime = classJoinTime + timedelta(minutes=60)

        if (currentTime.time()>=classJoinTime.time()) and (currentTime.time()<=classEndTime.time()):
            return True
        else:
            return False



    # finding the joining link for particular class
    def checkLinkAvailability(self,driver, classJoinName, nextClassJoinTime, defaultTabId):
        global LOCK
        spanToBeOpened = ""
        linkNotAvailable = True
        timeRemainsForNextClass = True
        firstTime = True

        while(linkNotAvailable and timeRemainsForNextClass):

            # Checking if connection is Available or not
            networkAvaliable = connectionCheck()
            if not networkAvaliable:
                is_connected()

            while(True):
                if not LOCK:
                    LOCK = True
                    driver.switch_to.window(defaultTabId)
                    break
                else:
                    logging.info("Waiting for other tabs to finish their task")
                    time.sleep(2)
            

            driver.get('https://cuchd.blackboard.com/ultra/course')


            if firstTime:
                firstTime=False

                # finding which class to join
                while(networkAvaliable):
                    try:
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//h4[@title='{classJoinName.upper()}']"))).click()
                        break
                    except:
                        logger.error("Unable to open the current Lecture")
                        is_connected()
                        driver.refresh()
            else:
                is_connected()
                driver.refresh()


            # Checking if connection is Available or not
            networkAvaliable = connectionCheck()
            if not networkAvaliable:
                is_connected()

            
            # opening dropdown to find class joining button
            while(networkAvaliable):
                try:
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='sessions-list-dropdown']"))).click()
                    break
                except:
                    logger.error("Unable to Locate the session")
                    is_connected()
                    driver.refresh()
            

            html_page = driver.page_source
            classes_avaliable = list()
            soup = bs4(html_page,features="lxml")


            # finding class joining button
            for tag in soup.findAll("a",{"role":"menuitem"}):
                span_text = (str(tag.text))[1:-1]
                if (str(span_text)!=str('Course Room')) and ('Visible to students' not in span_text) and ('Hidden from students' not in span_text):
                    classes_avaliable.append(span_text)  


            currentTime = datetime.now()


            if len(classes_avaliable)>=1:
                linkNotAvailable = False
                spanToBeOpened = classes_avaliable[0]


            if(currentTime.time()>=nextClassJoinTime.time()):
                timeRemainsForNextClass = False
            
            time.sleep(30)

        LOCK = False

        if not linkNotAvailable:
            return [True,spanToBeOpened]
        else:
            return [False,""]



class JoinOnlineClass(Thread):
    def __init__(self, tabId, defaultTabId, driver, lectureName, nextClassJoinTime):
        Thread.__init__(self)
        self.tabId = tabId
        self.defaultTabId = defaultTabId
        self.driver = driver
        self.lectureName = lectureName
        self.nextClassJoinTime = nextClassJoinTime



    def run(self):
        global LOCK, bbPermissionFlag
        timeElapsed = 0
        currentTime = datetime.now().time()
        logger.info(f"Attending class {self.lectureName} at {currentTime}")


        # Switching to the class tab
        while(True):
            if not LOCK:
                LOCK = True
                self.driver.switch_to.window(self.tabId)
                break
            else:
                logging.info("Waiting for other tabs to finish their task")
                time.sleep(2)
        

        # Checking if connection is Available or not
        networkAvaliable = connectionCheck()
        if not networkAvaliable:
            is_connected()


        # check if audio and video persmissions are given or not
        if(not bbPermissionFlag):
            bbPermissionFlag = True
            audioTestFlag=False

            while(networkAvaliable):
                    try:
                        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Yes. Audio is working.']"))).click()
                        audioTestFlag = True
                    except:
                        logger.error("Exception 1 occured in Audio Testing.")
                        
                    if not audioTestFlag:
                        try:
                            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Skip audio test']"))).click()
                        except:
                            logger.error("Exception 2 occured in Audio Testing.")
                            is_connected()
                            self.driver.refresh()
                            
                         
                    try:
                        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Yes. Video is working.']"))).click()
                    except:
                        logger.error("Error in providing Video permission to BB")
                        is_connected()
 
                    try:
                        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Later']"))).click()
                    except:
                        logger.error("Error in providing permission to BB")
                        is_connected()

                    try:
                        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Close']"))).click()
                        break
                    except:
                        logger.error("Error in providing permission to BB")
                        is_connected()

        LOCK = False
                        
        # waiting in class till next class and minimum 60 minutes
        timeSpentInWait = 0
        while(True):
            
            # check if current time is greater than next class time and minimum time in class is greater than 60 minutes
            if(timeElapsed>=3600):
                break
            else:
                # Checking if connection is Available or not
                networkAvaliable = connectionCheck()
                if not networkAvaliable:
                    is_connected()
                    while(True):
                        if not LOCK:
                            LOCK = True
                            self.driver.switch_to.window(self.tabId)
                            self.driver.refresh()                                   #Reconnecting
                            LOCK = False
                            break
                        else:
                            logging.info("Waiting for other tabs to finish their task")
                            time.sleep(2)
                            timeSpentInWait+=2


            # Checking if Moderator removed you form class
            try:
                self.driver.find_element_by_xpath("//h1[text()='A moderator removed you']")
                logger.warning("Moderator removed you form class.")
                break
            except:
                pass


            time.sleep(15)
            timeElapsed+=15
        

        # Switching to the class tab
        while(True):
            if not LOCK:
                LOCK = True
                self.driver.switch_to.window(self.tabId)
                self.driver.close()
                LOCK = False
                break
            else:
                logging.warning("Waiting for other tabs to finish their task")
                time.sleep(2)
        

        # converting total class joined seconds to minutes
        total_class_time_min = (timeElapsed-timeSpentInWait) /60
        logger.warning("Attended " + self.lectureName + " Lecture for: " + str(total_class_time_min) + " minutes")