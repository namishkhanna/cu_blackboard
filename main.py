import os, time
from pathlib import Path
from datetime import datetime
from packages.miscellaneous import GetUserDetails,is_connected, connectionCheck, logger
from packages.uims import UimsManagement
from packages.BB import ClassManagement, LoginBB, JoinOnlineClass
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# global variables
global USERDATAFILENAME, TIMETABLE, CHROMEPATH

USERDATAFILENAME = "userData.txt"
TIMETABLE = "rptStudentTimeTable.csv"

temp = str(os.path.normpath("\\AppData\\local\\Google\\Chrome\\User Data\\Default"))
CHROMEPATH = str(Path.home()) + temp





if __name__ == '__main__':

    # Geting user details
    getDetailsOBJ = GetUserDetails(USERDATAFILENAME)
    userDetails = getDetailsOBJ.getDetails()
    userName = userDetails['username']
    password = userDetails['password']
    if userDetails["failInput"]:
        exit()

    # Getting details from UIMS
    uimsManagementOBJ = UimsManagement(TIMETABLE,userName,password,CHROMEPATH)
    if not os.path.isfile(TIMETABLE):
        uimsManagementOBJ.getDetailsFromUIMS()

    # Reading all user details from csv file
    allDetails = uimsManagementOBJ.loadDetailsFromFIle()

    BbClassManagementOBJ = ClassManagement()
    lecturesToAttend = BbClassManagementOBJ.fromWhichLecture(allDetails)

    # Logging into BB Account
    BbLoginOBJ = LoginBB(userName,password,CHROMEPATH)
    driver = BbLoginOBJ.loginBB()

    IsLastClass = False
    # Looping through all Lectures
    for index in range(lecturesToAttend-1,len(allDetails)):
        classJoinTime = BbClassManagementOBJ.joinClassDetails(allDetails[index])
        classJoinName = (allDetails[index])[1]
        nextClassJoinTime = BbClassManagementOBJ.nextClassDetails(allDetails[index])
        total_class_time = 0

        currentTime = datetime.strptime(f"{datetime.now().time()}","%H:%M:%S.%f")
        logger.info("Waiting for class ....")
        if currentTime<classJoinTime:
            timeTowait = classJoinTime - currentTime
            timeTowait = timeTowait.total_seconds()
            print()
            while timeTowait: 
                mins, secs = divmod(timeTowait, 60)
                hrs, mins = divmod(mins,60)
                timer = '{:02d}:{:02d}:{:02d}'.format(int(hrs), int(mins), int(secs)) 
                print("Time remaining for the class: ",timer, end="\r") 
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
                    break
                except:
                    logger.error(f"Unabale to join class: {classJoinName}. Retrying ....")
                    is_connected()
            
            joinClassOBJ = JoinOnlineClass(driver.window_handles[-1],driver.window_handles[0],driver,classJoinName,nextClassJoinTime)
            joinClassOBJ.start()

        
        # if time to attend lecture is gone and link is not available    
        elif not IsLinkAvailable[0]:
            print("Class Joining Link for " + classJoinName + " Lecture Not Found !!!")
            classtojoin = False

        # check if time for class is gone or not
        elif not IsTimeToJoinClass:
            logger.critical(f"You missed lecture for: {classJoinName}")
        
    driver.close()
    exit()


            
        