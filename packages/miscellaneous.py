import  socket, logging, time, coloredlogs, os, sys



logger = logging.getLogger(__name__)
coloredlogs.install(fmt='%(asctime)s [%(levelname)s]: %(message)s',level='DEBUG', logger=logger)



global LOCK, bbPermissionFlag, BROWSERS
LOCK = False
bbPermissionFlag = False
BROWSERS = ["Google Chrome","Mozilla Firefox","Brave"]



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



def signal_handling(signum,frame):
    
    counter=0
    while(True):
        counter+=1
        try:
            choice = str(input("\nDo you really want to exit the program(y/n): ")).lower().strip()
        except:
            pass
        print()
        if choice:
            choice = choice[0]
            if choice=='y':       
                sys.exit()
            elif (choice!='y') and (choice!='n'):
                logger.warning("Enter a valid input (y or n) !!!")
            elif choice=='n':
                break
        else:                
            logger.warning("Enter a valid input (y or n) !!!")

        if counter==3:
            logger.warning("3 Failed attempts. Exiting ")      
            sys.exit()



def threeFailedInputs():
    logger.warning("3 Failed inputs. Exiting.....")
    input()
    sys.exit()



def fiveFailedAttempts():
    logger.warning("5 Failed attempts. Exiting.....")
    input()
    sys.exit()
            
    

class GetUserDetails():
    def __init__(self, userFileName):
        self.userFileName = userFileName



    def getDetails(self):
        # If user inputs multiple wrong inputs
        failInput = False
        tempCounter = 0
        hasChangedDetails = False


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
                input()
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
                input()
                exit()


            msg = f"The avaliable user details are: username: {USERNAME}    Password: {PASSWORD}"
            logger.info(msg)
            choice = 'n'
            counter = 0


            while(choice!='y'):
                counter+=1
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
                            hasChangedDetails=True
                        except:
                            msg = f"Unable to write user details to disk: {self.userFileName}"
                            logger.error(msg)
                            logger.info("Exiting the program")
                            input()
                            exit()

                        choice='y'

                    elif ((choice!='y') and (choice!='n')):
                        logger.warning("Enter a valid choice !!! (y/n) ")  


                else:
                    logger.warning("Enter a valid choice !!! (y/n) ")
                    # Assigning some value to variable. So that it does not goes in infinite loop
                    choice = 'n' 


                if counter==3:
                    logger.warning("3 failed attempts. Exiting.")
                    input()
                    exit()                                                       


            msg = f"Continuing with: username: {USERNAME}    Password: {PASSWORD}"
            logger.info(msg)

        return {'username':USERNAME,'password':PASSWORD, 'failInput':failInput, 'hasChangedDetails':hasChangedDetails}



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
            input()
            exit()
            
        return {'username':USERNAME, 'password':PASSWORD, 'failInput':failInput}
