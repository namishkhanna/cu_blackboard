import  socket, logging, time, coloredlogs, os

logger = logging.getLogger(__name__)
coloredlogs.install(fmt='%(asctime)s [%(levelname)s]: %(message)s',level='DEBUG', logger=logger)

global LOCK, bbPermissionFlag
LOCK = False
bbPermissionFlag = False

# check if device is connected to internet
def connectionCheck():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            sock.close
        return True
    except:
        pass

        
    return False

def is_connected():

    # waiting till network connection is available
    tempCounter = 0
    networkAvaliable = connectionCheck()
    if not networkAvaliable:
        logger.error("Network not available")

    while(not networkAvaliable):

        tempCounter+=1
        if tempCounter == 7:
            logger.info("Waiting for internet connection ...")
        time.sleep(2)
        
        networkAvaliable = connectionCheck()


class GetUserDetails():
    def __init__(self, userFileName):
        self.userFileName = userFileName

    def getDetails(self):
        # If user inputs multiple wrong inputs
        failInput = False
        tempCounter = 0

        if not os.path.isfile(self.userFileName):
            USERNAME = str(input("Enter Username: "))
            PASSWORD = str(input("Enter Password: "))
            
            tempCounter = 0
            while((len(USERNAME)<=0) and (len(PASSWORD)<=0)):
                USERNAME = str(input("Enter Username: "))
                PASSWORD = str(input("Enter Password: "))
                tempCounter+=1
                if tempCounter == 3:
                    logger.error("3 Failed attempts. Exiting .....")
                    failInput = True

            try:
                with open(self.userFileName,'w',encoding="utf8") as f:
                    f.write(USERNAME+" ")
                    f.write(PASSWORD)
            except:
                msg = f"Unable to write user details to disk: {self.userFileName}"
                logger.error(msg)
                logger.info("Exiting the program")
                exit()

        else:
            try:
                with open(self.userFileName,'r',encoding='utf8') as f:
                    data = (str(f.read())).split(" ")
                    USERNAME = data[0]
                    PASSWORD = data[1]
            except:
                msg = f"Unable to read file: {self.userFileName}"
                logger.error(msg)
                logger.info("Exiting the program")
                exit()
            msg = f"The avaliable user details are: username: {USERNAME}    Password: {PASSWORD}"
            logger.info(msg)

            choice = 'n'
            while(choice!='y'):
                print()
                choice = str(input("Continue with same login details(y/n): ")).lower().strip()
                print()

                if choice:
                    choice=choice[0]

                    if choice=='n':                                                                     # if user has new login details
                        USERNAME=""
                        PASSWORD=""

                        tempCounter=0
                        while((len(USERNAME)<=0) and (len(PASSWORD)<=0)):
                            USERNAME = str(input("Enter Username: "))
                            PASSWORD = str(input("Enter Password: "))
                            tempCounter+=1
                            if tempCounter == 3:
                                logger.error("3 Failed attempts. Exiting .....")
                                failInput = True

                        try:
                            with open(self.userFileName,'w',encoding="utf8") as f:
                                f.write(USERNAME+" ")
                                f.write(PASSWORD)
                        except:
                            msg = f"Unable to write user details to disk: {self.userFileName}"
                            logger.error(msg)
                            logger.info("Exiting the program")
                            exit()

                        choice='y'

                    elif ((choice!='y') and (choice!='n')):
                        logger.warning("Enter a valid choice !!! (y/n) ")  

                else:
                    logger.warning("Enter a valid choice !!! (y/n) ")
                    # Assigning some value to variable. So that it does not goes in infinite loop
                    choice = 'n'                                                        

            msg = f"Continuing with: username: {USERNAME}    Password: {PASSWORD}"
            logger.info(msg)

        return {'username':USERNAME,'password':PASSWORD, 'failInput':failInput}

    def getCorrectDetails(self):
        USERNAME=""
        PASSWORD=""

        # If user inputs multiple wrong inputs
        failInput = False
        tempCounter = 0

        while((len(USERNAME)<=0) and (len(PASSWORD)<=0)):
                USERNAME = str(input("Enter Username: "))
                PASSWORD = str(input("Enter Password: "))
                tempCounter+=1
                if tempCounter == 3:
                    logger.error("3 Failed attempts. Exiting .....")
                    failInput = True
        try:
            with open(self.userFileName,'w',encoding="utf8") as f:
                f.write(USERNAME+" ")
                f.write(PASSWORD)
        except:
            msg = f"Unable to write user details to disk: {self.userFileName}"
            logger.error(msg)
            logger.info("Exiting the program")
            exit()
            
        return {'username':USERNAME, 'password':PASSWORD, 'failInput':failInput}