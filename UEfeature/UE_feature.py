import pymysql
import numpy as np
import re
import base64
import time
#<时间，UE标识、操作类型、操作结果，当前所属阶段,次数>
judge_value = ["imsi", "suci", "supi", "urn:uuid"]

#需要一个字典：完整的描述所有的URL{"url":{"id":xxx,"decscription":"","status":""},}
#这个URL是简化处理之后的URL
url_info = {
    "nnrf-discv1nf-instancesrequester-nf-typeexisttarget-nf-typeexist": {"stage": "", "kind": "bg"},
    "nausf-authv1ue-authentications": {"stage": "register", "kind": "UE"},
    "nausf-authv1ue-authenticationssuci5g-aka-confirmation": {"stage": "register", "kind": "UE"},
    "nnrf-discv1nf-instancesrequester-nf-typeexistservice-namesexisttarget-nf-typeexist": {"stage": "", "kind": "bg"},
    "nudm-ueauv1sucisecurity-informationgenerate-auth-data": {"stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsiauthentication-dataauthentication-subscription": {"stage": "register", "kind": "UE"},
    "nudm-ueauv1imsiauth-events": {"stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsiauthentication-dataauthentication-status": {"stage": "register", "kind": "UE"},
    "nnrf-discv1nf-instancesrequester-nf-typeexistsupiexisttarget-nf-typeexist": {"stage": "register", "kind": "UE"},
    "nudm-sdmv1imsinssaiplmn-idexist": {"stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsinumberprovisioned-dataam-datasupported-features": {"stage": "register",
                                                                                      "kind": "UE"},
    "nudm-uecmv1imsiregistrationsamf-3gpp-access": {"stage": "register", "kind": "UE"},
    "nudm-sdmv1imsiam-dataplmn-idexist": {"stage": "register", "kind": "UE"},
    "nudm-sdmv1imsismf-select-dataplmn-idexist": {"stage": "register", "kind": "UE"},
    "nudm-sdmv1imsiue-context-in-smf-data": {"stage": "register", "kind": "UE"},
    "nudm-sdmv1imsisdm-subscriptions": {"stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsicontext-dataamf-3gpp-access": {"stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsinumberprovisioned-dataam-datasupported-featuresexist": {"stage": "register",
                                                                                           "kind": "UE"},
    "nudr-drv1subscription-dataimsinumberprovisioned-datasmf-selection-subscription-datasupported-features": {
        "stage": "register", "kind": "UE"},
    "nudr-drv1subscription-dataimsicontext-datasmf-registrationssupported-features": {"stage": "register",
                                                                                      "kind": "UE"},
    "nudr-drv1subscription-dataimsicontext-datasdm-subscriptions": {"stage": "register", "kind": "UE"},
    "npcf-am-policy-controlv1policies": {"stage": "register", "kind": "UE"},
    "nudr-drv1policy-datauesimsiam-data": {"stage": "register", "kind": "UE"},
    "nnssf-nsselectionv1network-slice-informationnf-idexistnf-typeexistslice-info-request-for-pdu-sessionexist": {
        "stage": "register", "kind": "UE"},

    "nnrf-discv1nf-instancesdnnexistrequester-nf-typeexistservice-namesexistsnssaisexisttarget-nf-typeexisttarget-plmn-listexist": {
        "stage": "PDU SetUp", "kind": "bg"},
    "nsmf-pdusessionv1sm-contexts": {"stage": "PDU SetUp", "kind": "UE"},
    "nudm-sdmv1imsism-datadnnexistplmn-idexistsingle-nssaiexist": {"stage": "PDU SetUp", "kind": "UE"},
    "nudr-drv1subscription-dataimsinumberprovisioned-datasm-datasingle-nssaiexist": {"stage": "PDU SetUp",
                                                                                     "kind": "UE"},
    "npcf-smpolicycontrolv1sm-policies": {"stage": "PDU SetUp", "kind": "UE"},
    "nnrf-discv1nf-instancesrequester-nf-typeexisttarget-nf-instance-idexisttarget-nf-typeexist": {"stage": "PDU SetUp",
                                                                                                   "kind": "bg"},
    "namf-commv1ue-contextsimsin1-n2-messages": {"stage": "PDU SetUp", "kind": "UE"},
    "nsmf-pdusessionv1sm-contextsurn:uuidmodify": {"stage": "PDU SetUp", "kind": "UE"},

    "nsmf-pdusessionv1sm-contextsurn:uuidrelease": {"stage": "deregister", "kind": "UE"},
    "npcf-am-policy-controlv1policiesimsi": {"stage": "deregister", "kind": "UE"}

}
#pymysql连接数据库
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='5gc',
                             charset='utf8mb4')


def urlparase(url):  # 解析URL来得到网元,返回请求端/响应端网元,中间使用哈希做计算对应关系
    """
    解析传递过来的URL
    返回值：
    useful_url：一个list，返回有用的url部分；
    param：一个map,url中提取到的参数，即?后的部分
    key_slice：一个list，是param这个map的key的list，之前使用Golang写的，这一个可以不要
    """
    # 需要清空一下global_param里的数据
    url_level = url.split("/")  # 还要新建一个数组，存储处理之后的元素
    last_url_part = url_level[len(url_level) - 1]  # 获取到最后一个url信息
    useful_url = getuseful_url(url_level)
    param, key_slice = param_parase(last_url_part)
    # 对上述信息进行合并
    return useful_url, param, key_slice#param：参数map，key_slice:map的遍历顺序，useful_url:有用的url

def getuseful_url(url_level):  # 对第一层级“/”的url做解析;返回有效的url
    """
    提取URL中的有用URL
    参数
    url_level:分割之后的URL的list
    返回值
    useful_url：有用的URL list，这里将URL中的imsi-20893xxx替换成imsi,suci-xxx替换成suci
    """
    useful_url = []
    for i in range(0, len(url_level)):
        # 是否是最后一个元素
        if i == len(url_level) - 1:  # 是的话，需要做split
            url_last=url_level[i].split("?")[0]
            res = judge_contains(url_last)
            if res != "NO":
                useful_url.append(res)
            else:
                useful_url.append(url_last)# 看了一下最后一个貌似不会有数据，大错特错，会有的
        else:  # 不是的话，需要判断是否包含imsi,urn:uuid，pdusession,suci,supi
            res = judge_contains(url_level[i])
            if res != "NO":
                useful_url.append(res)
            else:
                useful_url.append(url_level[i])
    return useful_url


def judge_contains(strings):  # 需要判断是否是全数字字符串
    """
    判断字符串中是否是纯数字/是否包含imsi,suci,supi,urnuuid等信息
    参数:
    strings:传入的字符串
    返回值:
    字符串"imsi","suci","number"等
    """
    for i in range(len(judge_value)):
        if strings.find(judge_value[i]) >= 0:  # 包含有用信息，待处理
            return judge_value[i]
        elif judge_int(strings) == True:
            return "number"
    return "NO"


def judge_int(strings):
    """
    判断数字是否是int类型
    """
    try:
        strings = float(strings)  # 可能回出现问题
    except:
        return False
    return True


def param_parase(last_url_part):  # 返回一个map
    """
    解析URL"/"分割之后的最后一段，得到有用的参数
    参数：
    last_url_part:最后一段URL参数
    返回值：
    result：一个参数map
    key_slice：参数map的key list
    """
    key_slice = []
    result = {}
    # 判断是否存在参数?
    if last_url_part.find("?") >= 0:
        last_url_part = last_url_part.split("?")[1]

    else:
        last_url_part = ""
    paramstr_list = last_url_part.split("&")
    for i in range(len(paramstr_list)):
        part_res = paramstr_list[i].split("=")
        key_slice.append(part_res[0])
        if len(part_res) == 2:
            result[part_res[0]] = part_res[1]
        elif len(part_res) == 1:
            result[part_res[0]] = ""
    return result, key_slice


def concat(useful_url, param, key_slice):  # 这个函数的返回值是唯一的，可以对应到唯一的索引
    concat_str = ""
    for i in range(len(useful_url)):
        print(useful_url[i])
        concat_str += useful_url[i]
    for key in key_slice:
        concat_str += key
        # print(key)
        # print(param[key])
        if len(param[key]) != 0:
            concat_str += "exist"
    return concat_str


def link_mysql_geturl():
    cursor = connection.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(
        "SELECT id,time,srcip,srcport,desip,desport,url,method,status,reqheader,reqbody,resheader,resbody FROM traffic_field order by time limit 1000,3000")
    # cursor.execute(
    #     "SELECT * FROM traffic_field")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchall()
    cursor.close()
    res = np.array(data)
    result=[]
    for item in res:
        result.append({"id":item[0],"time":item[1],"srcip":item[2],"srcport":item[3],"desip":item[4],
                       "desport":item[5],"url":item[6],"method":item[7],"status":item[8],"reqheader":item[9],
                       "reqbody":str(base64.b64decode(item[10])),"resheader":item[11],
                       "resbody":str(base64.b64decode(item[12]))})
    return result

def judge_exists(table, key, value):
    cursor = connection.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(
        "SELECT count(*) FROM " + table + " where " + key + "='" + value + "'")
    num = cursor.fetchone()
    cursor.close()
    if num != 0:
        return True
    return False


def insert_without_condition(table, key, value):
    cursor = connection.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(
        "insert into  " + table + " (" + key + ") values " + "('" + value + "')")
    cursor.close()
    connection.commit()


def insert_with_condition(table, key, value, condition_key, condition_value):
    cursor = connection.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(
        "update " + table + " set " + key + " = " + "'" + value + "'" + " where " + condition_key + " = " + "'" + condition_value + "'")
    cursor.close()
    connection.commit()


def update_with_condition(table, key, value, condition_key, condition_value):
    cursor = connection.cursor()
    print("update " + table + " set " + key + " = " + "concat(IFNULL(" + key + ",'')," + "';" + value + "'" + ")" + " where " + condition_key + " = " + "'" + condition_value + "'")

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute(
        "update " + table + " set " + key + " = " + "concat(IFNULL(" + key + ",'')," + "\";" + value + "\"" + ")" + " where " + condition_key + " = " + "'" + condition_value + "'")
    cursor.close()
    connection.commit()

# 从一个字符串中找到对应的东西
def find_param(strings, key):
    reg = re.findall(key + "(.*?)(\"|,|;|&|/|')",strings)
    # print(reg)
    if len(reg) == 0:
        return ""
    temp_str = reg[0]
    result = temp_str[0: len(temp_str) - 1]
    print(key+result[0])

    return key+result[0]

# find_param("'urn:uuid:1212'","urn:uuid:")

def get_param():
    #处理url，找到对应的存在的param名称，调用find_param进行查找
    sql_results = link_mysql_geturl()
    # url_concat_list=[]
    suci_map = {}
    imsi_map = {}
    urnuuid_map = {}
    for sql_results_value in sql_results:
        #输出url
        print("__________________________________________________")
        print(sql_results_value["url"]) # 这个url需要进行判断

        res1, res2, res3 = urlparase(sql_results_value["url"])
        concat_url = concat(res1, res2, res3)
        # url_concat_list.append(concat_url)
        # 找到url, reqbody, resbody, resheader
        suci = find_param(sql_results_value["url"]+"/"+sql_results_value["reqbody"]+"/"+sql_results_value["resbody"]+"/"+sql_results_value["resheader"], "suci-")
        imsi = find_param(sql_results_value["url"]+"/"+sql_results_value["reqbody"]+"/"+sql_results_value["resbody"]+"/"+sql_results_value["resheader"], "imsi-")
        urnuuid = find_param(sql_results_value["url"]+"/"+sql_results_value["reqbody"]+"/"+sql_results_value["resbody"]+"/"+sql_results_value["resheader"], "urn:uuid:")
        #fmt.Println("\n\n")
        #进行存储
        if suci != "" and imsi == "" :#只有suci, 查看是否存在当前suci，若不存在就插入suci
            # if not suci in suci_map.keys():# 不存在当前suci
            insert_without_condition("transfer", "suci", suci)
            suci_map[suci] = True
            update_with_condition("transfer", "stage", str(stage_info(sql_results_value,concat_url)), "suci", suci)
        elif suci != "" and imsi != "":# 同时有suci和imsi：建立对应关系, 查看是否存在suci，若存在，则更新对应的imsi(可能需要告警)
            if suci in suci_map.keys():# suci必须存在
                insert_with_condition("transfer", "imsi", imsi, "suci", suci)
                imsi_map[imsi] = True
            update_with_condition("transfer", "stage", str(stage_info(sql_results_value,concat_url)), "suci", suci)
        elif suci == "" and imsi != "" and urnuuid == "":# 只有imsi, 查看是否存在imsi，不存在则插入(可能需要告警)
            if imsi.count("-")==2:
                imsi_list=imsi.split("-")
                imsi=imsi_list[0]+"-"+imsi_list[1]

            if not imsi in imsi_map.keys() :# imsi不可以不存在
                print("error 1")
                print(imsi)
            update_with_condition("transfer", "stage", str(stage_info(sql_results_value,concat_url)), "imsi", imsi)
        elif suci == "" and imsi != "" and urnuuid != "":# 同时有imsi和urnuuid:建立对应关系，插入urn: uuid
            if imsi in imsi_map.keys():# imsi必须存在
                insert_with_condition("transfer", "urnuuid", urnuuid, "imsi", imsi)
                urnuuid_map[urnuuid] = True
            update_with_condition("transfer", "stage", str(stage_info(sql_results_value,concat_url)), "imsi", imsi)
        elif suci == "" and imsi == "" and urnuuid != "":# 只有urn:uuid->此时urn: uuid不能为空，查看是否存在urn: uuid(不存在需要告警)
            if not urnuuid in urnuuid_map.keys():
                print("error 2")
            update_with_condition("transfer", "stage", str(stage_info(sql_results_value,concat_url)), "urnuuid", urnuuid)

    # set_all=set()
    # for ele in url_concat_list:
    #     set_all.add(ele)
    #     print(ele)
    # print(set_all)

def stage_info(info_dict,URL):#返回一个list，包括数据：<时间，源IP：端口，目的IP：端口，操作类型，操作结果，当前所属阶段,次数>
    """

    """
    time, srcIP, desip, srcport, desport, method, status=info_dict['time'], info_dict['srcip'],info_dict['desip'], info_dict['srcport'],info_dict['desport'],info_dict['method'], info_dict['status']
    stage_list=[]
    stage_list.append(time)
    stage_list.append(srcIP+":"+srcport)
    stage_list.append(desip+":"+desport)
    stage_list.append(URL)
    stage_list.append(method)
    stage_list.append(status)
    stage_list.append(url_info[URL]["stage"])#当前所属阶段，暂时置空
    stage_list.append(0)#count数值，暂时置空
    return stage_list
# start=time.time()
# get_param()
# print(time.time()-start)




