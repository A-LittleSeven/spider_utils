from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyautogui


class login_taobao(object):
    """
    淘宝爬虫测试  
    目标是获取cookie   
    """
    def __init__(self, account, passwd, timeout=10, ptn = (920, 530), args=None):
        """
        account: 登录账号\n
        passwd: 登录密码\n
        timeout: 等待元素加载的时间\n  
        ptn: 定位滑块的位置，使用鼠标定位\n   
        distance: 定位滑块的滑动距离\n
        """
        self.account = account 
        self.passwd = passwd
        self.timeout = timeout
        # use to adjust position when screen is differet
        self.X, self.Y = ptn
        # drag distance set to 280
        self.distance = 280
        self.options  = Options()
        # self.chrome_options.add_argument('--headless')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.brow = webdriver.Chrome(chrome_options = self.options)
        self.brow.set_window_size(1600, 900)
        self.lgnLink = 'https://login.taobao.com/'
    
    def loginTest(self):
        """
        淘宝登录测试   
        用户行为模拟加参数selenium尝试解决
        """
        self.brow.get(self.lgnLink)
        loginBtn = By.XPATH('//*[@id="J_Quick2Static"]')
        # wait for element to be clickable
        WebDriverWait(self.brow, self.timeout, 0.5).until(EC.element_to_be_selected(loginBtn))
        self.brow.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
        time.sleep(0.9756)
        self.brow.find_element_by_xpath('//*[@id="TPL_username_1"]').send_keys(self.account)
        time.sleep(0.5536)
        self.brow.find_element_by_xpath('//*[@id="TPL_password_1"]').send_keys(self.passwd)
        self.brow.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()
        # captcha show
        try:
            brow.find_element_by_xpath('//*[@id="nc_1_n1z"]').is_display()

        except Exception as e :
            print(e)
            pass

if __name__ == "__main__":
    test = login_taobao()
    test.loginTest()