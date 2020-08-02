# -*- coding:utf-8 -*-
# __author__ = WilsonLee
from __future__ import division
from __future__ import print_function

from selenium import webdriver
from requests import Session
from lxml import etree
import os
import pickle
import re
import time
import math
import random
import csv
import pymysql

try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass


# ----config of mysql----
host = '127.0.0.1'
usname = 'root'
paswd = ''
database = ''
# ----end of config----


header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}


def mysql_SetUp():
    try:
        db = MySQLdb.connect(host, usname, paswd, database,
                             use_unicode=0, charset='gb2312')
        cur = db.cursor()
        return db, cur
    except Exception as e:
        print(e)


def login_Weibo(username, pwd):

    url = 'http://weibo.cn'
    try:
        brow = webdriver.Chrome()
    except:
        pass

    brow.get(url)
    time.sleep(3)
    onclick_login = brow.find_element_by_xpath('/html/body/div[2]/div/a[1]')
    onclick_login.click()
    time.sleep(3)
    login_user = brow.find_element_by_xpath('//*[@id="loginName"]')
    login_user.click()
    login_user.send_keys(username)
    login_pwd = brow.find_element_by_xpath('//*[@id="loginPassword"]')
    login_pwd.click()
    login_pwd.send_keys(pwd)
    login_btm = brow.find_element_by_xpath('//*[@id="loginAction"]')
    login_btm.click()
    time.sleep(5)
    time.sleep(5)
    try:
        # 获取Cookies
        if not "cookies" in os.listdir('.'):
            with open('cookies', 'wb') as fp:
                cookies = brow.get_cookies()
                fp.write(pickle.dumps(cookies))
                brow.close()

        return True

    except Exception as e:
        return(e)

def start_Session(username, password):
    mysession = Session()
    if not 'cookies' in os.listdir('.'):
        login_Weibo(username, password)
    else:
        try:
            with open('cookies', 'rb') as fp:
                cookies = pickle.loads(fp.read())
                for cookie in cookies:
                    mysession.cookies.set(cookie['name'], cookie['value'])
            return mysession
        except Exception as e:
            return e

# 手动修改排序规则
def search_weibo(sess, keywords, sortedby='hot'):

    url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword={}&sort={}&page='.format(
        keywords, sortedby)

    cmp_div = re.compile('<div class="c" id="M_.*?>(.*?)<div class="s">')
    cmp_page = re.compile('pas')
    s = time.time()
    count = 0
    for page in range(1, 80):
        if page % 2 == 0:  # 休眠策略，根据时间调整
            time.sleep(random.randint(7, 18))
        if page % 100 == 0:
            time.sleep(20)
        new_url = url + str(page)
        with open('url', 'a') as fp:
            fp.write(new_url)
            fp.write('\n')
        try:
            res = sess.get(new_url, headers=header)
            res.encoding = res.apparent_encoding
            content = res.content.encode('gbk', 'ignore')
        except Exception as e:
            print(e)

        div_page = re.findall(cmp_div, content)
        for i in div_page:
            count += 1
            with open('weibo_content.csv', 'a') as fp:
                # 在这里写入数据
                file = csv.writer(fp)
                file.writerow([
                    parserContent(i)[0],
                    parserContent(i)[1],
                    parserContent(i)[2],
                    parserContent(i)[3],
                    parserContent(i)[4],
                    parserContent(i)[5],
                    parserContent(i)[6],
                    parserContent(i)[7]
                ])
    sp = time.time()
    use_time = (sp - s)
    print(use_time, count)

def parserContent(string):
    # 原创内容
    regex_ID = re.compile('<a class="nk".*?>(.*?)</a>', re.S)
    regex_Weibo = re.compile('<span class="ctt">(.*?)&nbsp;', re.S)
    regex_time = re.compile('<span class="ct">(.*?)&nbsp;')
    regex_device = re.compile('<span class="ct">.*?&nbsp;(.*?)</span>')
    regex_likes = re.compile(
        '<a href="http[s]?://weibo.cn/attitude.*?>(.*?)</a>')
    regex_repost_link = re.compile(
        '(http[s]?://weibo.cn/repost.*?)">(.*?)</a>')
    regex_comment_link = re.compile(
        '(http[s]?://weibo.cn/comment.*?)" class="cc">(.*?)</a>')
    try:
        Id = re.findall(regex_ID, string)[0].decode('gbk', 'ignore')
    except:
        Id = None
    try:
        Weibo = re.sub('<a href.*?>|</a>|<b.*?>|&nbsp|\n|\s|<img src.*?>|<span.*?>|</span>|;',
                       '', re.findall(regex_Weibo, string)[0]).decode('gbk', 'ignore')
    except:
        Weibo = None
    try:
        like = re.findall(regex_likes, string)[0].decode('gbk', 'ignore')
    except:
        like = None
    try:
        timeStamp = re.findall(regex_time, string)[0].decode('gbk', 'ignore')
    except:
        timeStamp = None
    try:
        Device = re.findall(regex_device, string)[0].decode('gbk', 'ignore')
    except:
        Device = None
    try:
        repost_Link, repost_Num = re.findall(regex_repost_link, string)[0]
        repost_Num = repost_Num.decode('gbk', 'ignore')
    except:
        repost_Link, repost_Num = None, None
    try:
        comment_Link, comment_Num = re.findall(regex_comment_link, string)[0]
        comment_Num = comment_Num.decode('gbk', 'ignore')
    except:
        comment_Link, comment_Num = None, None
    return Id, Weibo, like, repost_Num, repost_Link, comment_Num, comment_Link, timeStamp, Device


def parserComment(sess, url):

    url = re.sub('&amp;|#cmtfrm', '', url)

    regex_pages = re.compile('<input name="mp".*?value="(.*?)".*?>')
    regex_div = re.compile('<div class="c" id="C_.*?>(.*?)</div>')
    regex_id = re.compile('<a href.*?>(.*?)</a>')
    regex_comment = re.compile('<span class="ctt">(.*?)</span>')
    regex_timestamp = re.compile('<span class="ct">&nbsp;(.*?)&nbsp;')

    res = sess.get(url, headers=header)
    res.encoding = res.apparent_encoding
    try:
        pages = re.findall(regex_pages, res.content)[0]
    except:
        pages = 10

    for page in range(1, 10):
        if page % 3 == 0:  # 休眠策略，根据时间调整
            time.sleep(random.randint(10, 18))
        if page % 100 == 0:
            time.sleep(random.randint(20, 60))
        if page % 502 == 0:
            time.sleep(random.randint(300, 500))

        new_url = url + u'&page={}'.format(page)
        try:
            res = sess.get(new_url, headers=header)
            res.encoding = res.apparent_encoding
            content = res.content.encode('gbk', 'ignore')
        except Exception as e:
            print(e)

        div_page = re.findall(regex_div, content)

        for i in div_page:
            try:
                ida = re.findall(regex_id, i)[0].decode('gbk', 'ignore')
            except:
                ida = None
            try:
                comment = re.sub('<a href.*?>|</a>|<b.*?>|&nbsp|\n|\s|<img src.*?>|<span.*?>|</span>|"|;',
                                 '', re.findall(regex_comment, i)[0]).decode('gbk', 'ignore')
            except:
                comment = None
            try:
                timestamp = re.findall(regex_timestamp, i)[0]
            except:
                timestamp = None

            with open('weibo_comment.csv', 'a') as fp:
                wt = csv.writer(fp)
                wt.writerow(
                    [ida,
                     comment,
                     timestamp]
                )


if __name__ == '__main__':

    print (u"************************工具介绍***************************")
    print ("\n")
    print (u"   1.该工具可实现对微博的数据进行搜索")
    print (u"   2.在爬取数据之前，需要按照提示对使用的微博账号进行登录")
    print (u"   3.在爬取数据之前需要输入爬取的关键字")
    print ("\n")

    # -----config of user and password-----
    account = u''
    pasword = u''
    # -----end of config-----
    if not 'cookies' in os.listdir('.'):
        if account == '' or pasword == '':
            account = raw_input(u'请输入微博账号：'.encode('gbk'))
            pasword = raw_input(u'请输入微博密码：'.encode('gbk'))

    # -----insert keyword-----
    keyword = u''.encode('gbk')
    # -----endl-----
    if keyword == '':
        keyword = raw_input(u'请输入爬取关键字：'.encode('gbk')).decode('gbk', 'ignore')

    sess = start_Session(account, pasword)
    search_weibo(sess, keyword)
    
