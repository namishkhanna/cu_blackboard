from pathlib import Path
from datetime import datetime
import os, time, signal, requests
from packages.uims import UimsManagement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from packages.BB import ClassManagement, LoginBB, JoinOnlineClass
from packages.miscellaneous import GetUserDetails,is_connected, connectionCheck, logger,BROWSERS, signal_handling, threeFailedInputs



# global variables
global USERDATAFILENAME, TIMETABLE, CHROMEPATH



CURRENT_VERSION = "v4.0"
USERDATAFILENAME = "userData.txt"
TIMETABLE = "rptStudentTimeTable.csv"
temp = str(os.path.normpath("\\AppData\\yal\\Google\\Chrome\\User Data\\Default"))
CHROMEPATH = str(Path.home()) + temp
signal.signal(signal.SIGINT,signal_handling)



if __name__ == '__main__':

    version = requests.get("https://api.github.com/repos/namishkhanna/cu_blackboard/releases").json()[0]
    version = version["tag_name"]

    if(CURRENT_VERSION == version):
        # Geting user details
        getDetailsOBJ = GetUserDetails(USERDATAFILENAME)
        userDetails = getDetailsOBJ.getDetails()
        userName = userDetails['username']
        password = userDetails['password']
        if userDetails["failInput"]:
            input()
            exit()

        
        if (userDetails['hasChangedDetails']) and (os.path.isfile(TIMETABLE)):
            os.remove(TIMETABLE)


        # select Browser Name
        selectedBrowser = BROWSERS[0]
        print()
        print("Select your browser: ")
        for i in range(len(BROWSERS)):
            print(f"{i+1}.    {BROWSERS[i]}")
        print()
        counter = 0
        while(True):
            counter+=1
            try:
                temp = int(input("Enter your browser choice: "))
                temp-=1
                break
            except:
                logger.warning("Enter a valid choice !!")
                logger.info("Input can only be a number.")
            if counter==3:
                threeFailedInputs()
        selectedBrowser = BROWSERS[temp]
        print()


        # Getting details from UIMS
        uimsManagementOBJ = UimsManagement(TIMETABLE,userName,password,CHROMEPATH, selectedBrowser)
        if not os.path.isfile(TIMETABLE):
            uimsManagementOBJ.getDetailsFromUIMS()


        # Reading all user details from csv file
        allDetails = uimsManagementOBJ.loadDetailsFromFIle()
        BbClassManagementOBJ = ClassManagement()
        lecturesToAttend = BbClassManagementOBJ.fromWhichLecture(allDetails)


        # Logging into BB Account
        logger.info("Logging into Black Board")
        BbLoginOBJ = LoginBB(userName,password,CHROMEPATH, selectedBrowser)
        driver = BbLoginOBJ.loginBB()


        IsLastClass = False
        # Looping through all Lectures
        for index in range(lecturesToAttend-1,len(allDetails)):
            classJoinTime = BbClassManagementOBJ.joinClassDetails(allDetails[index])
            classJoinName = (allDetails[index])[1]
            nextClassJoinTime = BbClassManagementOBJ.nextClassDetails(allDetails[index])
            total_class_time = 0

            currentTime = datetime.strptime(f"{datetime.now().time()}","%H:%M:%S.%f")
            if (currentTime<classJoinTime):
                nextClassTemp = str(index+1) + ": " + allDetails[index][0] + " " + allDetails[index][1]
                logger.info("Waiting for class ....")
                timeTowait = classJoinTime - currentTime
                timeTowait = timeTowait.total_seconds()

                print()
                while (timeTowait>0):
                    currentTime = datetime.strptime(f"{datetime.now().time()}","%H:%M:%S.%f")
                    timeTowait = classJoinTime - currentTime
                    timeTowait = timeTowait.total_seconds()
                    mins, secs = divmod(timeTowait, 60)
                    hrs, mins = divmod(mins,60)
                    timer = '{:02d}:{:02d}:{:02d}'.format(int(hrs), int(mins), int(secs)) 
                    print(f"Time remaining for the class: [{nextClassTemp}]:\t",timer, end="\r") 
                    time.sleep(1) 
                    timeTowait -= 1
                print()

            
            # checking if class joining link is available or not
            IsLinkAvailable = BbClassManagementOBJ.checkLinkAvailability(driver, classJoinName, nextClassJoinTime,driver.window_handles[0])


            # checking if class time is less than next class time
            IsTimeToJoinClass = BbClassManagementOBJ.compareTime(classJoinTime)

            
            if IsTimeToJoinClass and IsLinkAvailable[0]:
                # Checking if connection is Available or not
                networkAvaliable = connectionCheck()
                
                if not networkAvaliable:
                    is_connected()

                while(networkAvaliable):
                    try:
                        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{IsLinkAvailable[1]}']"))).click()
                        time.sleep(5)
                        break
                    except:
                        logger.error(f"Unabale to join class: {classJoinName}. Retrying ....")
                        is_connected()
                        
                joinClassOBJ = JoinOnlineClass(driver.window_handles[-1],driver.window_handles[0],driver,classJoinName,nextClassJoinTime)
                joinClassOBJ.start()

            
            # if time to attend lecture is gone and link is not available    
            elif not IsLinkAvailable[0]:
                logger.error("Class Joining Link for " + classJoinName + " Lecture Not Found !!!")
                classtojoin = False


            # check if time for class is gone or not
            elif not IsTimeToJoinClass:
                logger.critical(f"You missed lecture for: {classJoinName}")


        logger.info("Waiting for all classes to end .....")
        joinClassOBJ.join()
            

        driver.quit()
        input()
        exit()
    
    else:
        logger.error("Update Required !!!")
        logger.info("Download the Latest Version from https://github.com/namishkhanna/cu_blackboard/releases/")
        input()
