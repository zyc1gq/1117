#计算统计特征，每个网元20秒时间段的数据
#计算得到：1.最大值；2.最小值；3.数据包数量；4.数据包总和大小；5.数据包平均大小；6.TCP交互数量；7.网元ID；8.数据包的方差；

import pymysql
import json
import numpy as np
connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='5gc',
                                     charset='utf8mb4')
nf_list=[["192.168.2.14","27017"],["192.168.2.4","29510"],["192.168.2.13","29504"],["192.168.2.7","29503"],["192.168.2.9","29502"],["192.168.2.5","29507"],["192.168.2.2","29509"],["192.168.2.10","29518"],["192.168.2.3","29531"]]

def sql_to_sql():
    nfID_list,max_list,min_list,ave_list,fc_list,num_list,all_list,tcp_num_list,tcpnumsize_list=[],[],[],[],[],[],[],[],[]
    i=0
    for item in nf_list:
        json_dict=[]
        #查询IP:端口的记录的第一条数据的timestamp,按照时间递增去查找20s内的所有数据
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = connection.cursor()

        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT time_stamp from tcp_fields where src='"+item[0]+"' and srcport='"+item[1]+"' limit 1")

        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchall()
        timestamp=data[0][0]
        print(timestamp)
        timestamp=int(timestamp)

        # 再次查询IP:端口：streamindex_list相同的
        # 使用 execute()  方法执行 SQL 查询
        for index in range(timestamp,timestamp+10*180,10):
            # cursor.execute("SELECT len,streamindex from tcp_fields where ((src='"+item[0]+"' and srcport="+item[1]+") or (dst='"+item[0]+"' and dstport="+item[1]+"))"+" and time_stamp>"+str(int(index))+" and time_stamp<"+str(int(index)+10))
            cursor.execute("SELECT len,streamindex from tcp_fields where dst='"+item[0]+"' and dstport="+item[1]+" and time_stamp>"+str(int(index))+" and time_stamp<"+str(int(index)+10))

            # 使用 fetchone() 方法获取数据.
            data = cursor.fetchall()
            res = np.array(data)
            # print(res)
            # print(res[:,0])
            len_list=res[:,0].tolist()
            # print(len(len_list))
            streamindex_num=len(list(set(res[:,1].tolist())))
            # print(streamindex_num)
            nfID_list.append(i)
            max_list.append(max(len_list))
            min_list.append(min(len_list))
            ave_list.append(np.mean(len_list))
            fc_list.append(np.var(len_list))
            num_list.append(len(len_list))
            all_list.append(sum(len_list))
            tcp_num_list.append(streamindex_num)
            tcpnumsize_list.append(sum(len_list)/streamindex_num)
            # print(max(len_list))
        print(i)
        i+=1

    return nfID_list,max_list,min_list,ave_list,fc_list,num_list,all_list,tcp_num_list,tcpnumsize_list

def to_sql(nfID_list,max_list,min_list,ave_list,fc_list,num_list,all_list,tcp_num_list,tcpnumsize_list):
    for i in range(len(nfID_list)):
        # try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建SQL语句
            sql = "insert into tcp_stat_sx_req (nfID,max,min,ave,fc,num,allnum,tcpnum,tcpnumsize) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            # 执行SQL语句
            cursor.execute(sql, (nfID_list[i],max_list[i],min_list[i],int(ave_list[i]),int(fc_list[i]),num_list[i],all_list[i],tcp_num_list[i],tcpnumsize_list[i]))
            #提交
            connection.commit()

nfID_list,max_list,min_list,ave_list,fc_list,num_list,all_list,tcp_num_list,tcpnumsize_list=sql_to_sql()
to_sql(nfID_list,max_list,min_list,ave_list,fc_list,num_list,all_list,tcp_num_list,tcpnumsize_list)