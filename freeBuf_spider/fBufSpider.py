# -*- coding:utf-8 -*-
from lxml import etree
import requests
import re
import lxml
import time
import pymysql
import random
import os
import logg
import traceback
import mysql_helper


class FreeBuf(object):
    """
    freebuf文章爬虫，先抓取全部链接然后根据链接抓取所有的文章内容
    :param:host: db_host
    :param:user: db_user
    :param:passwd: db_password
    :param:database: db_database
    :return: none
    """
    def __init__(self, host, user, passwd, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.sleepTime = 30
        # define a log handler
        self.logger = logg.logg.logHandler()
        self.queue = []
        # seed
        self.seed = 'https://www.freebuf.com/articles/page/%s'

    def _mysql_init(self):
        try:
            db = pymysql.connect(self.host, self.user,
                                 self.passwd, self.database)
            cur = db.cursor()
            return cur, db
        except Exception as e:
            print(e)


    def _fakeUserAgent(self):
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 71.0 .3578 .98 Safari / 537.36 ',
            ''
        ]
        ua = random.choice(ua_list)
        return ua


    def _fedQueue(self):
        
        cur, db = self._mysql_init()
        try:
            fetchLK = """SELECT link FROM linkqueue WHERE iscrawled=0 LIMIT 30"""
            cur.execute(fetchLK)
            linkqueue = cur.fetchall()
        except Exception as e:
            self.logger.error(traceback.format_exc(e))
        if linkqueue == () and self.queue == []:
            db.close()
            self.logger.info('FBuf: There is no data left to crawl, the program goes to sleep mode, sleep time : %s'%self.sleepTime)
            time.sleep(60 * self.sleepTime)
        else:
            for i in linkqueue:
                cur.execute('UPDATE linkqueue SET iscrawled=1 WHERE link="%s"' % (i))
                db.commit()
                self.queue.append(i)
        db.close()


    def getlink(self):

        cur, db = self._mysql_init()
        uA = {"User-Agnet": self._fakeUserAgent()}
        c_regex = re.compile('<div class="news-img">(.*?)</div>')
        l_regex = re.compile('href="(.*?)"')

        # page大概400页定500上限无数据返回可以手动停止
        for i in range(1, 500):

            if i == 5:
                break

            nlink = self.seed % i
            try:
                res = requests.get(nlink, headers=uA)
                res.encoding = res.apparent_encoding
            except Exception as e:
                self.logger.warning('page %s 抓取失败' %i, '失败原因:', traceback.format_exc())
                # time.sleep(60 * 2)
                continue

            res_c = re.findall(c_regex, res.text)

            for cdata in res_c:
                llink = re.findall(l_regex, cdata)[0]
                print(llink)
                llsql = """INSERT INTO linkQueue(link, iscrawled) VALUES ('%s', %d) """
                try:
                    cur.execute(llsql % (llink, 0))
                    db.commit()
                except Exception as e:
                    self.logger.warning(traceback.format_exc())
                    continue

            # time.sleep(random.randrange(4,7))


    def lparser(self):

        cur, db = self._mysql_init()
        uA = {"User-Agnet": self._fakeUserAgent()}

        while(True):
            if len(self.queue) < 5:
                self._fedQueue()
            else:
                lk_toc = self.queue.pop()[0]
                try:
                    cpmt = requests.get(lk_toc, headers=uA)
                    cpmt.encoding = cpmt.apparent_encoding
                except Exception as e:
                    self.logger.warning(traceback.format_exc())
                    self.queue.append(lk_toc)
                    continue

                dom = etree.HTML(cpmt.content)
                querydata = []
                try:  # aquire content of article
                    title = ''.join(re.sub(
                        '\s+', '', dom.xpath('//*[@id="getWidth"]/div[2]/div/div[1]/h2//text()')[0]))
                except:
                    title = 'missing'
                try:
                    author = dom.xpath('//*[@id="getWidth"]/div[2]/div/div[1]/div/span[1]/a//text()')[0]
                except:
                    author = 'missing'
                try:
                    wt_time = dom.xpath('//*[@id="getWidth"]/div[2]/div/div[1]/div/span[3]//text()')[0]
                except:
                    wt_time = 'missing'
                try:
                    looked = int(dom.xpath('//*[@id="getWidth"]/div[2]/div/div[1]/div/span[4]//text()')[1])
                except:
                    looked = 0
                try:
                    tag = dom.xpath('//*[@id="getWidth"]/div[2]/div/div[1]/div/span[5]/a//text()')[0]
                except:
                    tag = 'missing'
                try:
                    content = ''.join(re.sub('\s+?', '', i) for i in (dom.xpath('//*[@id="contenttxt"]//text()')))
                except:
                    content = 'lost'

                querydata.append((title, author, looked, wt_time, tag, content))  # data storage
                insql = """INSERT INTO datastore(title, author, looked, ctime, tag, content) 
                            VALUES ("%s", "%s", "%s", "%s", "%s", "%s")"""
                try:
                    cur.executemany(insql, querydata)
                    db.commit()
                    break
                except Exception as e:
                    self.logger.warning(traceback.format_exc())
                    continue


if __name__ == "__main__":

    #mysql> create database netsecure
    host = '127.0.0.1'
    user = 'root'
    passwd = 'admin123'
    db ='testdb'
    port = 3306
    mysql_helper.database_init(host, user, passwd, port, db)
    import time
    import threading

    Fspider = FreeBuf(host, user, passwd, db)
    # 抓取链接
    # threading.Thread()
    # Fspider.getlink()

    s_time = time.time()
    # 根据队列链接抓取内容
    Fspider.lparser()
    p_time = time.time()
    print(p_time - s_time)
