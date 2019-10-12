from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import requests
import base64
import cv2
import pickle
import time
import re
import io


class loginJd(object):
    """
    某东验证码绕过
    """
    def __init__(self, account, passwd, timeout=None, args=None):
        # read the account and the passwd
        self.account = account
        self.passwd = passwd
        self.timeout = timeout
        self.chrome_options  = Options()
        # self.chrome_options.add_argument('--headless')
        self.brow = webdriver.Chrome(chrome_options = self.chrome_options)
        self.brow.set_window_size(1600, 900)
        self.lgnLink = 'https://passport.jd.com/new/login.aspx'

    def __del__(self):
        self.brow.close()

    def loginChain(self):
        self.brow.get(self.lgnLink)
        time.sleep(2.1223)
        # change the login way into input way
        self.brow.find_element_by_xpath(
            '//*[@id="content"]/div[2]/div[1]/div/div[3]/a').click()
        time.sleep(1.2335)
        self.brow.find_element_by_xpath('//*[@id="loginname"]').send_keys(self.account)
        time.sleep(0.996)
        self.brow.find_element_by_xpath('//*[@id="nloginpwd"]').send_keys(self.passwd)
        loginBTN = self.brow.find_element_by_xpath('//*[@id="loginsubmit"]')
        time.sleep(0.5677)
        loginBTN.click()
        time.sleep(0.557)

        # deal with the captcha
        try:
        # to deal with the situation if there exists no captcha
            self.brow.find_element_by_xpath('//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]')
            resmsg = self.slideBar(5)
            print(resmsg)
        except Exception as  e:
            print("cannot load the captcha")
            print(e)
        # >>>>>>>>>>>>>>>>>>>>>>>s
        # dump the cookies for spider
        cookies = pickle.dumps(self.brow.get_cookies())
        with open("%s.txt" % int(time.time()), 'wb') as cookjar:
            cookjar.write(cookies)


    def slideBar(self, retries = 3):
        """
        滑动验证码解决 \n
        参数: 重试次数 \n
        """
        if retries:
            # if there still has captcha, perform
            try:
                if self.brow.find_element_by_xpath('//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]'):
                    regex = re.compile(',(.*?)">')
                    bigimg = self.brow.find_element_by_xpath(
                        '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[1]/img'
                        ).get_property('outerHTML')
                    bigimgb64Buffer = re.findall(regex, bigimg)[0]
                    target = self._b64imgdecoder('target', bigimgb64Buffer)
                    smallimg = self.brow.find_element_by_xpath(
                        '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div[2]/img'
                        ).get_property('outerHTML')
                    smallimgb64Buffer = re.findall(regex, smallimg)[0]
                    slider = self._b64imgdecoder('slider', smallimgb64Buffer)
                    offset = loginJd.process_captcha(slider, target)
                    # time.sleep(3.1233)
                    tag_element = self.brow.find_element_by_xpath(
                        '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]')
                    time.sleep(0.071)
                    self._drag_and_drop_by_offset(tag_element, offset)
                    time.sleep(0.8755)
                    return self.slideBar(retries - 1)
            except:
                return "certificate success"
        else :
            return "certificate failed, please retries later"

    def _drag_and_drop_by_offset(self, tag_element, offset):
        """
        创建一个随机操作 \n
        输入: tag_element(需要拖拽的元素), offset(偏移量) \n
        输出: None \n
        """
        def ease_out_expo(x):
            if x == 1:
                return 1
            else:
                return 1 - pow(2, -10 * x)
        
        def get_tracks(distance, seconds):
            tracks = [0]
            offsets = [0]
            for t in np.arange(0.0, seconds, 0.1):
                offset = round(ease_out_expo(t/seconds) * distance)
                tracks.append(offset - offsets[-1])
                offsets.append(offset)
            return offsets, tracks
        
        _, tracks = get_tracks(offset, 1.4)
        ActionChains(self.brow).click_and_hold(tag_element).perform()
        for x in tracks:
            ActionChains(self.brow).move_by_offset(x, 0).perform()
        ActionChains(self.brow).release().perform()

    def _b64imgdecoder(self, name, imgBuffer):
        """
        decode网站的验证码图片 \n
        输入: name(本地图片名称), imgBuffer(加密的验证码流) \n
        输出: imgBufferDecoder(解密过的文件流) \n
        """
        if not isinstance(imgBuffer, bytes):
            imgBuffer = imgBuffer.encode('utf-8')
        # decode b64String buffer
        imgBufferDecoder = base64.decodebytes(imgBuffer)
        with open('%s.png' % name, 'wb') as target:
            target.write(imgBufferDecoder)
        return imgBufferDecoder

    @staticmethod
    def process_captcha(slider, target):
        """
        从文件流读取验证码图片与缺块图片并且返回缺块图片的
        偏移量 \n
        输入: File流, slider(缺块图片)，target(验证码图片) \n
        输出: offset(缩放过后的图像偏移量)
        """
        if isinstance(slider, bytes):
            # feed in bytes io
            sdr_img = cv2.imdecode(np.frombuffer(slider, np.uint8), cv2.IMREAD_GRAYSCALE)
            tgt_img =  cv2.imdecode(np.frombuffer(target, np.uint8), cv2.IMREAD_GRAYSCALE)
            tgtsource = cv2.imdecode(np.frombuffer(target, np.uint8), cv2.IMREAD_COLOR)
        else:
            # for test feed the png object
            sdr_img, tgt_img = cv2.imread(slider, 0), cv2.imread(target, 0)
            tgtsource = cv2.imread(target)

        _, sdr_thres = cv2.threshold(sdr_img, 0 , 255, cv2.THRESH_BINARY_INV)
        tgt_mat = np.asarray(tgt_img)
        avgLumin = np.mean(tgt_mat, dtype=int)
        # set the threshold for picture
        thres = avgLumin - 62
        _, tgt_thres = cv2.threshold(tgt_img, thres, 255, cv2.THRESH_BINARY)
        res = cv2.matchTemplate(tgt_thres, sdr_thres, cv2.TM_CCORR_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        left_up = max_loc
        right_down = (left_up[0] + 50, left_up[1] + 50)
        cv2.rectangle(tgtsource, left_up, right_down, (0,255,0), 1)
        # reset this param if could not match the pattern
        scale = 0.77
        offset = left_up[0] * scale
        return int(offset)


if __name__ == "__main__":
    # test login
    test = loginJd('','')
    test.loginChain()
    # loginJd.process_captcha('slider.png')
