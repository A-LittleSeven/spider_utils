import cv2
import numpy as np



"""
解决滑块验证码的思路与方法:
首先滑块验证码分为两个部分, 滑块和目标图片
目标是定位缺失图块在图像中的位置, 使用cv的模板匹配算法
"""
def process_captcha(slider, target):
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
    # cv2.imshow("000", sdr_thres)
    tgt_mat = np.asarray(tgt_img)
    avgLumin = np.mean(tgt_mat, dtype=int)
    # set the threshold for picture
    thres = avgLumin - 62
    _, tgt_thres = cv2.threshold(tgt_img, thres, 255, cv2.THRESH_BINARY)
    # cv2.imshow("111", tgt_thres)
    res = cv2.matchTemplate(tgt_thres, sdr_thres, cv2.TM_CCORR_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    left_up = max_loc
    right_down = (left_up[0] + 50, left_up[1] + 50)
    cv2.rectangle(tgtsource, left_up, right_down, (0,255,0), 1)
    cv2.imshow()
    # reset this param if could not match the pattern
    scale = 0.79
    offset = left_up[0] * scale
    return int(offset)