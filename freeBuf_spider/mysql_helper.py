# -*- coding=utf8 -*-
import pymysql


def database_init(host, user, password, port, database):
    """
    :param:host: db_host
    :param:user: db_user
    :param:passwd: db_password
    :param:database: db_database
    :return: none
    """
    print('NatSecure -- Mysql init start --')
    try:
        conn = pymysql.connect(host = host, user = user, passwd = password, port = port, db = database)
        cur = conn.cursor()
    except Exception as e:
        raise(e)

    # create jobqueue
    _cque = '''create table if not exists linkQueue(id int(10) not null auto_increment, link varchar(150) not null comment "抓取文章链接", iscrawled int(1) not null default 0 comment "是否已经抓取", ctime timestamp comment "抓取时间", primary key(id), unique key(link)) default charset="utf8"'''

    try:
        cur.execute(_cque)   
        conn.commit()
    except Exception as e:
        print('NatSecure -- LinkQueue Already Exist --', e)
    
    print('NatSecure -- LinkQueue init -- Success --')
    
    # create data storege   
    _cdata = '''create table if not exists dataStore(id int(10) not null auto_increment, title varchar(50) not null comment "文章标题", author varchar(20) not null comment "作者", looked int(8) not null comment "围观数", ctime varchar(20) not null default 0 comment "文章创建时间", tag varchar(10) comment "标签", content text comment "文章内容", ptime timestamp comment "抓取时间", primary key(id)) default charset="utf8"'''

    try:
        cur.execute(_cdata)
        conn.commit()
    except Exception as e:
        print('NatSecure -- dataStore Alreadly Exist' , e)
    
    print('NatSecure -- dataStore init -- Success --')

    # cur.close()
    conn.close()


if __name__ == "__main__":
    # ------test init------
    host = 'localhost'
    user = 'root'
    password = 'admin123'
    port = 3306
    database = 'testdb'

    database_init(host, user, password, port, database)
    
