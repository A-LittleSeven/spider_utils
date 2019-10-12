from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import pickle


class login_taobao(object):
    """
    淘宝爬虫测试  
    目标是获取cookie   
    """
    def __init__(self, account, passwd, timeout=10):
        """
        :account: 登录账号

        :passwd: 登录密码

        :timeout: 等待元素加载的时间
        """
        self.account = account 
        self.passwd = passwd
        self.timeout = timeout
        self.options  = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
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
        # wait for js to Exec
        time.sleep(10)
        # inject
        self.brow.execute_script(open("./myFunc.js").read())
        print("success !")
        time.sleep(0.8823)
        try:
            self.brow.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
        except:
            pass
        time.sleep(3)
        time.sleep(0.9756)
        self.brow.find_element_by_xpath('//*[@id="TPL_username_1"]').send_keys(self.account)
        time.sleep(0.7536)
        self.brow.find_element_by_xpath('//*[@id="TPL_password_1"]').send_keys(self.passwd)
        time.sleep(0.9975)
        self.brow.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()
        time.sleep(3)
        #  dump cookies here >>>>>>>>>>>>>>>>>>>>>>
        print("yeaaaaah")

if __name__ == "__main__":
    test = login_taobao("", "")
    test.loginTest()
