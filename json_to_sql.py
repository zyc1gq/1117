#将json文件中需要的信息转储到mysql中
import json
import pymysql
connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='5gc',
                                     charset='utf8mb4')

def read_json():#从json中读取对应的字段，返回数据
    timestamp_list,src_list,dst_list,srcport_list,dstport_list,tcplen_list,payload_list,stream_list=[],[],[],[],[],[],[],[]
    with open("test.json","r") as load_f:
        load_dict=json.load(load_f)
    #遍历每一个load_dict中的元素，得到对应的数据
    for item in load_dict:
        try:
            tt=item["_source"]["layers"]["tcp"]["tcp.stream"]
            timestamp=item["_source"]["layers"]["frame"]["frame.time_epoch"]
            src=item["_source"]["layers"]["ip"]["ip.src"]
            dst = item["_source"]["layers"]["ip"]["ip.dst"]
            srcport=item["_source"]["layers"]["tcp"]["tcp.srcport"]
            dstport = item["_source"]["layers"]["tcp"]["tcp.dstport"]
            tcplen=item["_source"]["layers"]["tcp"]["tcp.len"]
            payload=item["_source"]["layers"]["tcp"]["tcp.payload"]
            stream_index=item["_source"]["layers"]["tcp"]["tcp.stream"]
            # print(payload)
            timestamp_list.append(float(timestamp))
            src_list.append(src)
            dst_list.append(dst)
            srcport_list.append(int(srcport))
            dstport_list.append(int(dstport))
            tcplen_list.append(int(tcplen))
            if len(payload)>10000:
                payload=payload[:10000]
            payload_list.append(payload)
            stream_list.append(int(stream_index))

        except:
            continue
    return timestamp_list,src_list,dst_list,srcport_list,dstport_list,tcplen_list,payload_list,stream_list

def write_sql(timestamp_list,src_list,dst_list,srcport_list,dstport_list,tcplen_list,payload_list,stream_list):#将字段数据写入mysql
    print(len(src_list))
    for i in range(len(src_list)):
        try:
            # 获取会话指针
            with connection.cursor() as cursor:
                # 创建SQL语句
                sql = "insert into tcp_fields (time_stamp,src,srcport,dst,dstport,len,payload,streamindex) values(%s,%s,%s,%s,%s,%s,%s,%s)"
                # 执行SQL语句
                cursor.execute(sql, (timestamp_list[i], src_list[i],srcport_list[i],dst_list[i],dstport_list[i],tcplen_list[i],payload_list[i],stream_list[i]))
                #提交
                connection.commit()
        except:
            print(timestamp_list[i], src_list[i],srcport_list[i],dst_list[i],dstport_list[i],tcplen_list[i],payload_list[i],stream_list[i])
            continue


# timestamp_list,src_list,dst_list,srcport_list,dstport_list,tcplen_list,payload_list,stream_list=read_json()
# write_sql(timestamp_list,src_list,dst_list,srcport_list,dstport_list,tcplen_list,payload_list,stream_list)

#统计每一个IP:端口的使用次数

def read_json_max():#从json中读取对应的字段，返回数据
    fields_static={}
    with open("test.json","r") as load_f:
        load_dict=json.load(load_f)
    #遍历每一个load_dict中的元素，得到对应的数据
    i=0
    for item in load_dict:
        i+=1
        if i>20000:
            break
        try:
            tt=item["_source"]["layers"]["tcp"]["tcp.stream"]
            src=item["_source"]["layers"]["ip"]["ip.src"]
            dst = item["_source"]["layers"]["ip"]["ip.dst"]
            srcport=item["_source"]["layers"]["tcp"]["tcp.srcport"]
            dstport = item["_source"]["layers"]["tcp"]["tcp.dstport"]
            if src+":"+srcport+":"+dst+":"+dstport in fields_static.keys():
                fields_static[src+":"+srcport+":"+dst+":"+dstport]+=1
            elif dst+":"+dstport+":"+src+":"+srcport in fields_static.keys():
                fields_static[dst+":"+dstport+":"+src+":"+srcport] += 1
            else:
                fields_static[src + ":" + srcport + ":" + dst + ":" + dstport] = 1

            # if dst+":"+dstport in fields_static.keys():
            #     fields_static[dst+":"+dstport]+=1
            # else:
            #     fields_static[dst+":"+dstport] = 1

        except:
            continue
    res=sorted(fields_static.items(),key=lambda item:item[1])
    # print(res)
    real_res={}
    for key in fields_static.keys():
        keylist=key.split(":")
        if keylist[0]+":"+keylist[1] in real_res.keys():
            real_res[keylist[0]+":"+keylist[1]]+=1
        else:
            real_res[keylist[0] + ":" + keylist[1]] =1
        if keylist[2]+":"+keylist[3] in real_res.keys():
            real_res[keylist[2]+":"+keylist[3]]+=1
        else:
            real_res[keylist[2]+":"+keylist[3]] =1
    print(sorted(real_res.items(),key=lambda item:item[1]))

read_json_max()
