#分析sql中的数据进行统计，存入新的json文件中
#将每个网元的streamindex存成一条记录
#字段：ID，网元编号nfID，包数量pacnumber，包总和大小pacsize，平均大小，最大包大小maxsize,包长度序列
#nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list
from functools import reduce

import pymysql
import json
import numpy as np
connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='5gc',
                                     charset='utf8mb4')
nf_list=[["192.168.2.4","29510"],["192.168.2.13","29504"],["192.168.2.7","29503"],["192.168.2.9","29502"],["192.168.2.5","29507"],["192.168.2.2","29509"],["192.168.2.10","29518"],["192.168.2.3","29531"]]

def sql_to_sql():
    nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list=[],[],[],[],[],[]
    i=0
    for item in nf_list:
        json_dict=[]
        #查询IP:端口的记录，存为streamindex_list
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = connection.cursor()

        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT streamindex from tcp_fields where src='"+item[0]+"' and srcport='"+item[1]+"' limit 0,10000")

        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchall()
        res=np.array(data)
        streamindex_list=list(set(res[:,0].tolist()))

        #再次查询IP:端口：streamindex_list相同的
        # 使用 execute()  方法执行 SQL 查询
        for index in streamindex_list:
            cursor.execute("SELECT len from tcp_fields where src='"+item[0]+"' and srcport="+item[1]+" and streamindex="+str(index))

            # 使用 fetchone() 方法获取数据.
            data = cursor.fetchall()
            res = np.array(data)
            len_list=res[:,0].tolist()
            nfID_list.append(i)
            pacnum_list.append(len(len_list))
            pacsize_list.append(sum(len_list))
            avesize_list.append(sum(len_list)/len(len_list))
            maxsize_list.append(max(len_list))
            sql_list.append(str(len_list))
        i+=1
    return nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list

def to_sql(nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list):
    for i in range(len(nfID_list)):
        # try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建SQL语句
            sql = "insert into tcp_stat (nfID,pacnum,pacsize,avesize,maxsize,sql_list) values(%s,%s,%s,%s,%s,%s)"
            # 执行SQL语句
            cursor.execute(sql, (nfID_list[i],pacnum_list[i],pacsize_list[i],avesize_list[i],maxsize_list[i],sql_list[i]))
            #提交
            connection.commit()
        # except:
        #     print(nfID_list[i],pacnum_list[i],pacsize_list[i],avesize_list[i],maxsize_list[i],sql_list[i])
        #     continue




nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list=sql_to_sql()
to_sql(nfID_list,pacnum_list,pacsize_list,avesize_list,maxsize_list,sql_list)
