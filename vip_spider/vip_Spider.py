# -*- coding:utf-8 -*-
import configparser
import requests
import re
import pymysql
import chardet
import random
import json
import time
import logg
import sys


class VIP_Scrapy(object):

    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read('spider.conf')
        self.host = self.config['db_cp_product']['host']
        self.user = self.config['db_cp_product']['user']
        self.passwd = self.config['db_cp_product']['password']
        self.database = self.config['db_cp_product']['database']
        self.freq = int(self.config['update_freq']['time'])
        self.logger = logg.logg.logHandler()
        self.keyword_pipe = []
        self.params = {
            'keyword': '',
            'page': '',
            'count': 100,
            'suggestType': 'brand'
        }


    def _mysql_init(self):

        try:
            db = pymysql.connect(self.host, self.user,
                                 self.passwd, self.database)
            cur = db.cursor()
            return cur, db
        except Exception as e:
            self.logger.error(e)

    def _fakeUserAgent(self):

        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64; \
            Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; Win64; \
            x64) AppleWebKit / \
            537.36(KHTML, like Gecko) Chrome \
             / 71.0 .3578 .98 Safari / 537.36 '
        ]
        ua = random.choice(ua_list)
        return ua


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

    """
    def _ischeckUpdate(self):

        cur, db = self._mysql_init()
        cur.execute('SELECT update_time FROM db_competitor WHERE id=3')
        geUpdatetime = cur.fetchone()[0]
        now = int(time.time())
        if now - geUpdatetime >= self.freq:
            cur.execute('UPDATE db_grab_time SET \
                        last_spider_time=%s WHERE id=3' % (now))
            db.commit()
            db.close()
            return
        else:
            # add exit
            self.logger.info('爬取间隔小于设定时间，正在退出程序')
            db.close()
            sys.exit(0)
    """

    def _data_Processor(self, content, keyword, count):

        cur, db = self._mysql_init()
        regex_json_data = re.compile("\'suggestMerchandiseList\',\s+?(.*?)\);")
        encode_type = chardet.detect(content)
        content = content.decode(encode_type['encoding'])
        json_data = re.findall(regex_json_data, content)[0]
        json_data = json.loads(json_data)

        cur.execute('SELECT id FROM db_dict_brand WHERE name="%s"' %
                    (keyword))
        brand_id = cur.fetchone()


        if json_data['products'] == []:
            print("CURRENT TASK HAVE NO DATA LEFT TO CRAWL")
            return False, count

        for item in json_data['products']:
            try:
                querydata = []
                u_brand_id = brand_id
                u_prod_id = item['product_id']
                u_title = item['product_name']
                u_compid = '3'
                u_origin_price = item['price_info']['market_price_of_min_sell_price'] \
                    if not item['price_info']['market_price_of_min_sell_price'] \
                    == '' else '0'
                u_sale_price = item['price_info']['sell_price_min_tips']
                u_havetax = 0
                u_discountp = item['price_info']['vipshop_price']
                u_prod_time = 0
                u_desc = item['title_no_brand']
                u_img = item['small_image']
                u_ctime = int(time.time())
                u_utime = int(time.time())

                cur.execute('SELECT id FROM db_cp_product WHERE prod_id="%s" \
                AND comp_id=3' % (u_prod_id))     
                resdata = cur.fetchone()
                count += 1

                if resdata == None:
                    querydata.append((u_brand_id, u_prod_id, u_title,
                                      u_compid, u_origin_price,
                                      u_sale_price, u_havetax, u_discountp,
                                      u_prod_time, u_img, u_desc, u_ctime, u_utime))
                    insql = """
                            INSERT INTO db_cp_product (brand_id, prod_id, title, 
                            comp_id, orig_price, sale_price, tax_included, 
                            discount_price, prod_time, image, description, create_time, 
                            update_time) VALUES 
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                    try:
                        cur.executemany(insql, querydata)
                        db.commit()
                        self.logger.info(
                            'VIP Spider : Successfully insert data %s into database' % (u_prod_id))
                    except Exception as e:
                        self.logger.warning(e)
                        continue

                else:
                    upsql = """
                            UPDATE db_cp_product SET orig_price=%s, sale_price=%s,
                            discount_price = %s, update_time=%s WHERE id="%s"
                            """ % (u_origin_price, u_sale_price, u_discountp,
                                   int(time.time()), resdata[0])
                    try:
                        cur.execute(upsql)
                        db.commit()
                        self.logger.info(
                            'Kaola Spider: %s update successful!' % (resdata[0]))
                    except Exception as e:
                        self.logger.warning(e)
                        continue

            except Exception as e:
                self.logger.warning(e)
                continue

        db.commit()
        db.close()
        return True, count


    def access_Data(self, keyword):

        uA = {"User-Agent": self._fakeUserAgent()}
        url = 'https://category.vip.com/suggest.php'
        # define the Maximum pages
        pages = 48
        # start log 
        start_time = int(time.time())
        isNull, count = True , 0

        self.params['keyword'] = keyword

        for crawl_pages in range(pages + 1):

            if crawl_pages == 0:
                continue

            try:
                self.params['page'] = crawl_pages
                res = requests.get(url, params=self.params, headers=uA)
                res.encoding = res.apparent_encoding
                if isNull:
                    self.logger.info("VIP spider: crawling %s pages %d" \
                    % (keyword, crawl_pages))
                    isNull, count = self._data_Processor(res.content, keyword, count)
                    time.sleep(random.randint(13, 20))  
                else:
                    # print(count)
                    cur, db = self._mysql_init()
                    end_time = int(time.time())
                    cur.execute('SELECT id FROM db_dict_brand WHERE name="%s"' %
                                (keyword))
                    brand_id = cur.fetchone()

                    intoLog = '''INSERT INTO db_grab_log (grab_start_time,
                                grab_end_time, comp_id, brand_id, 
                                prod_count, status) VALUES
                                (%s, %s, %s, %s, %s, %s)
                            '''
                    cur.executemany(
                        intoLog, [(start_time, end_time, '2', brand_id, count, '0')])
                    db.commit()
                    self.logger.info(
                        'VIP Spider : Successfully update log for %s' % (keyword))
                    db.close()
                    return

            except Exception as e:
                self.logger.critical(e)
                sys.exit(1)


    def main(self):

        self._pipe_addKw()
        
        while(self.keyword_pipe):

            keyword = self.keyword_pipe.pop()
            self.access_Data(keyword)


if __name__ == "__main__":
   
    kl_demo = VIP_Scrapy()
    # kl_demo.access_Data('G&A')
    kl_demo.main()
