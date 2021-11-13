from sys import exc_info
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import random
from pathlib import Path
import datetime
from logging_utils import Logger
import argparse


class Presearch():
    def __init__(self):

        args = self.get_args()
        self.user_name = args.user_name
        self.password = args.password
        self.root = Path(args.root)

        self.login_page = 'https://presearch.org/login'
        self.search_page = 'https://presearch.org'

        self.keys = []
        lst = open('./search.txt').readlines()
        for word in lst:
            self.keys.append(word.split()[0])

        self.chromedriver_path = self.root.joinpath("chromedriver")

        self.max_search_no = args.max_search_no
        self.max_working_days = args.max_working_days 

        self._logger = self._make_logger(log_dir=self.root.joinpath(self.user_name))

    def get_args(self):

        parser = argparse.ArgumentParser(description="This script search in presearch engine to get reward tokens.",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--user_name", type=str, help="username to login to https://presearch.org/login")
        parser.add_argument("--password", type=str, help="password to login to https://presearch.org/login")
        parser.add_argument("--root", type=str, help="root to chrome")
        parser.add_argument("--max_search_no", type=int, default=60, help="max no of search to be done per day")
        parser.add_argument("--max_working_days", type=int, default=30, help="max days to search continuesly")
        args = parser.parse_args()

        return args

    def _get_options(self):

        # chrome option setting
        options = Options()
        options.add_argument(f"--user-data-dir={str(self.root)}/{self.user_name}/chrome-data")                              
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        options.add_argument(f"user-data-dir={str(self.root)}/{self.user_name}/chrome-data")                                

        return options

    def _make_logger(self, log_dir, logging_level='INFO', console_logger=True):

        logger = Logger(log_dir, logging_level=logging_level, console_logger=console_logger).make_logger()

        return logger
    
    def _process_start(self, driver, actions):
        search_key = random.choice(self.keys)
        success = False
        while not success:
            try:
                self.random_sleep()
                driver.get(self.search_page)                                                           
                driver.find_element_by_id("search").send_keys(search_key)
                driver.find_element_by_id("search").send_keys(Keys.ENTER)
                self._logger.info(f'Searching for "{search_key}"')
                self._perform_actions(actions)
                success = True
            except Exception:
                self._logger.warning(f'could not open {self.search_page}. Trying again...', exc_info=True)
                pass

        prev_search_key = search_key

        return driver, prev_search_key

    def _perform_actions(self, actions):
        """ Perform and reset actions """
        actions.perform()
        actions.reset_actions()
        for device in actions.w3c_actions.devices:
            device.clear_actions()
    
    def random_sleep(self):
        min_execution_time = 10 # min
        max_execution_time = 15 # min
        sleep_time = random.uniform(min_execution_time*60/self.max_search_no, max_execution_time*60/self.max_search_no)
        self._logger.info(f'sleeping for {sleep_time:.0f} seconds')
        time.sleep(sleep_time)

    def search(self):

        options = self._get_options()
        driver = webdriver.Chrome(chrome_options=options, executable_path=str(self.chromedriver_path))
        driver.implicitly_wait(25)  # seconds

        actions = ActionChains(driver)
        
        driver.get(self.login_page)                                                           
        time.sleep(15)

        
        actions.send_keys(self.user_name)
        actions.send_keys(Keys.TAB)
        actions.send_keys(self.password)
        self._perform_actions(actions)
        self._logger.info(input("Enter the captcha and press login button, then press 'ENTER/RETURN' in your keyboard: "))
        self._logger.info(f'Sign into {self.login_page}, username: {self.user_name}:')
                                                       
        driver, prev_search_key = self._process_start(driver, actions)

        counter = 1
        i = 1
        while i <= self.max_working_days:
            if counter < self.max_search_no:
                """ 
                ####################### OPTION1 #######################
                try:
                    self.random_sleep()
                    actions.send_keys(Keys.TAB * 2)
                    for j in range(len(prev_search_key)):
                        actions.send_keys(Keys.BACK_SPACE)
                    search_key = random.choice(self.keys)
                    actions.send_keys(search_key)
                    actions.send_keys(Keys.ENTER)
                    self._perform_actions(actions)
                    self._logger.info(f'Searching for "{search_key}"')
                    prev_search_key = search_key
                    counter += 1
                except:
                    self._logger.warning(f'could not search the new key.', exc_info=True)
                    driver, prev_search_key = self._process_start(driver, actions)
                    pass
                ####################### OPTION1 #######################
                """ 

                ####################### OPTION2 #######################
                driver, prev_search_key = self._process_start(driver, actions)
                counter += 1
                ####################### OPTION2 #######################

                # fliping a coin for random sleeping in priod of 4 to 7 seconds
                if random.randint(0, 1):     
                    sleep_time =random.uniform(4, 7)
                    self._logger.info(f'sleeping for {sleep_time:.2f} seconds')
                    time.sleep(sleep_time)  
            
            else:
                self._logger.info('maximum payable searches per day reached. Tokens info:')
                counter = 0
                try:
                    driver.get('https://presearch.org/account/tokens/rewards')
                    reward_tokens = driver.find_elements_by_class_name("tokens")[2].text
                    eligible_tokens = driver.find_elements_by_class_name("tokens")[1].text
                    self._logger.info(f'reward_tokens for {self.user_name}: {reward_tokens} PRE and eligible_tokens: {eligible_tokens} PRE')
                except Exception:
                    self._logger.warning('could not open https://presearch.org/account/tokens/rewards', exc_info=True)
                    pass

                if i == self.max_working_days:
                    self._logger.info(f'{self.max_working_days} day(s) search completed. Bye!')
                    break

                else:
                    self._logger.warning(f"I'm done for today, see you tommorrow...!")
                    time.sleep((random.uniform(24, 25)*60*60))                                                                                
                    driver, prev_search_key = self._process_start(driver, actions)
                    counter = 0
                    i += 1
                
                
        driver.close()



if __name__ == '__main__':
    presearch = Presearch()
    presearch.search()


# TODO: 
