# -*- coding:utf-8 -*-
import configparser
import logg
import requests
import re
import random
import json
import time
import pymysql
import sys


class xhs_Scrapy(object):

    def __init__(self):

        # read config
        self.config = configparser.ConfigParser()
        self.config.read('spider.conf')
        # config of mysql
        self.host = self.config['db_cp_product']['host']
        self.user = self.config['db_cp_product']['user']
        self.passwd = self.config['db_cp_product']['password']
        self.database = self.config['db_cp_product']['database']
        # define update frequency
        self.freq = int(self.config['update_freq']['time'])
        # define a log handler
        self.logger = logg.logg.logHandler()
        # define a keyword pipeline
        self.keyword_pipe = []
        self.params = {
            'sid': '',
            'keyword': '',
            'page': '',
            # noChange
            'per_page':	'20'
        }


    def _mysql_init(self):

        try:
            db = pymysql.connect(self.host, self.user,
                                 self.passwd, self.database)
            cur = db.cursor()
            return cur, db
        except Exception as e:
            self.logger.error(e)

    # add session_id get from Wechat
    def _sessionIDpool(self):
        
        sess = self.config['Session_list']['sess']
        sess_list = sess.split(',')
        sessid = random.choice(sess_list)
        return sessid

    # add User-Agent
    def _fakeUserAgent(self):

        ua_list = [
            'Mozilla/5.0 (Linux; Android 8.0.0; SM-G9350 Build/R16NW; wv) AppleWebKit/537.36 \
            (KHTML, like Gecko) Version / 4.0 Chrome / 66.0 .3359 .126 Mobile Safari / 537.36 \
            MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/appbrand0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 \
            (KHTML, like Gecko) Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN'
        ]
        ua = random.choice(ua_list)
        return ua

    # Not allowed outside the class
    # get words from brand table from mysql
    def _pipe_addKw(self):

        cur, db = self._mysql_init()
        try:
            fetchKW = "SELECT name FROM db_dict_brand WHERE status = 1"
            cur.execute(fetchKW)
            resdata = cur.fetchall()
            db.close()
        except Exception as e:
            self.logger.error(e)

        for i in resdata:
            self.keyword_pipe.append(i[0])


    def _checkUpdate(self):

        cur, db = self._mysql_init()
        cur.execute('SELECT update_time FROM db_competitor WHERE id=1')
        geUpdatetime = cur.fetchone()[0]
        now = int(time.time())
        if now - geUpdatetime >= self.freq:
            cur.execute('UPDATE db_competitor SET update_time=%s \
            WHERE id=1' % (now))
            db.commit()
            db.close()
            return
        else:
            db.close()
            sys.exit(0)


    def _data_insert(self, content, keyword, count):

        cur, db = self._mysql_init()
        json_data = json.loads(content)
        cur.execute('SELECT id FROM db_dict_brand WHERE name="%s"'\
        % (keyword))
        brand_id = cur.fetchone()


        if json_data[u'data'][u'items'] == []:
            print("CURRENT TASK HAVE NO DATA LEFT TO CRAWL")
            return False, count

        for item in json_data[u'data'][u'items']:
            querydata = []
            try:
                u_m_price = item[u'member_price']
            except:
                u_m_price = 0
            try:
                u_origin_price = item[u'price']
            except:
                u_origin_price = 0

            u_brand_id = brand_id
            u_prod_id = item[u'id']
            u_title = item[u'title']
            u_compid = '1'
            u_saleprice = item[u'item_price'][0]['price']
            u_havetax = item[u'tax_included']
            u_discountp = item[u'discount_price']
            u_favnum = item[u'fav_info'][u'fav_count']
            u_prod_time = item[u'time']
            u_desc = item[u'desc']
            u_feature = item[u'feature']
            u_img = item[u'image']
            u_glink = item[u'link']
            # commentcount =
            # commentgoodcount =
            u_canbuy = item[u'buyable']
            u_status = item[u'stock_status']
            u_ctime = int(time.time())
            u_utime = 0

            cur.execute('SELECT id FROM db_cp_product WHERE \
            prod_id="%s" AND comp_id=1' % (u_prod_id))
            resdata=cur.fetchone()

            count += 1 

            if resdata == None:

                querydata.append((u_brand_id, u_prod_id, u_title, u_compid,
                                    u_origin_price, u_saleprice, u_havetax,
                                    u_m_price, u_discountp, u_favnum,
                                    u_prod_time, u_desc, u_feature, u_img, u_glink,
                                    u_canbuy, u_status, u_ctime, u_utime))
                insql = """
                        INSERT INTO db_cp_product (brand_id, prod_id, title, 
                        comp_id, orig_price, sale_price, tax_included, 
                        member_price, discount_price, fav_count, prod_time, 
                        description, feature, image, goods_link, buyable, status, 
                        create_time, update_time) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                try:
                    cur.executemany(insql, querydata)
                    db.commit()
                    self.logger.info(
                            'Xiaohongshu Spider : Successfully insert data %s into database' % (u_prod_id))
                except Exception as e:
                    self.logger.warning(e)
                    continue
            else:
                upsql = """
                        UPDATE db_cp_product SET orig_price=%s, sale_price=%s,
                        member_price = %s, discount_price=%s, fav_count=%s, 
                        buyable=%s, status=%s, update_time=%s WHERE id="%s"
                        """ % (u_origin_price, u_saleprice, u_m_price,
                                u_discountp, u_favnum, u_canbuy, u_status,
                                int(time.time()), resdata[0])
                try:
                    cur.execute(upsql)
                    db.commit()
                    self.logger.info(
                        'Xiaohongshu Spider: %s update successful!' % (resdata[0]))
                except Exception as e:
                    self.logger.warning(e)
                    continue
           
        db.close()
        return True, count


    def access_Data(self, keyword):

        uA = {'User-Agent': self._fakeUserAgent()}
        sess_id = self._sessionIDpool()
        url = 'http://www.xiaohongshu.com/api/store/ps/products'
        # 定义爬取的最大页面数，如果页面数超过50则api不会返回数据
        pages = 51
        # start log
        start_time = int(time.time())
        isNull, count = True, 0

        self.params['sid'] = sess_id
        self.params['keyword'] = keyword

        for crawl_pages in range(pages + 1):

            if crawl_pages == 0:
                continue

            try:
                self.params['page'] = crawl_pages
                res = requests.get(url, params=self.params, headers=uA)
                res.encoding = res.apparent_encoding
                # is empty
                if isNull:
                    self.logger.info("Xiaohongshu spider: crawling %s pages %d" % (keyword, crawl_pages))
                    isNull, count = self._data_insert(res.content, keyword, count)
                    # 定义爬取间隔，修改爬取速度
                    time.sleep(random.randint(7, 20))
                else:
                    # print(count)
                    cur, db = self._mysql_init()
                    # add end log
                    end_time = int(time.time())
                    cur.execute('SELECT id FROM db_dict_brand WHERE \
                    name="%s"' % (keyword))
                    brand_id = cur.fetchone()

                    intoLog = '''INSERT INTO db_grab_log (grab_start_time,
                                grab_end_time, comp_id, brand_id, 
                                prod_count, status) VALUES
                                (%s, %s, %s, %s, %s, %s)
                            '''
                    cur.executemany(
                        intoLog, [(start_time, end_time, '1', brand_id, count, '0')])
                    db.commit()
                    self.logger.info('Xiaohongshu Spider : Successfully update log for %s'% (keyword))
                    db.close()
                    return

            except Exception as e:
                self.logger.error(e)
                sys.exit(1)

    
    def main(self):

        self._checkUpdate()
        self._pipe_addKw()
        
        # stop when list is null
        while(self.keyword_pipe):

            keyword = self.keyword_pipe.pop()
            self.access_Data(keyword)


if __name__ == "__main__":

    xhsdemo = xhs_Scrapy()
    # xhsdemo.access_Data('a2')
    xhsdemo.main()
