from UE_feature import *
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from UEfeatureService import UEfeature
from UEfeatureService import ttypes

from UEfeatureService import constants

__HOST = 'localhost'
__PORT = 9000

class UEfeatureHandler:
    def do_format(self,info_dict):#获取一个UE的一条信息
        suci_map = {}
        imsi_map = {}
        urnuuid_map = {}
        # 输出url
        print("__________________________________________________")
        print(info_dict["url"])  # 这个url需要进行判断

        res1, res2, res3 = urlparase(info_dict["url"])
        concat_url = concat(res1, res2, res3)
        # url_concat_list.append(concat_url)
        # 找到url, reqbody, resbody, resheader
        suci = find_param(
            info_dict["url"] + "/" + info_dict["reqbody"] + "/" + info_dict["resbody"] + "/" +
            info_dict["resheader"], "suci-")
        imsi = find_param(
            info_dict["url"] + "/" + info_dict["reqbody"] + "/" + info_dict["resbody"] + "/" +
            info_dict["resheader"], "imsi-")
        urnuuid = find_param(
            info_dict["url"] + "/" + info_dict["reqbody"] + "/" + info_dict["resbody"] + "/" +
            info_dict["resheader"], "urn:uuid:")
        # fmt.Println("\n\n")
        # 进行存储
        if suci != "" and imsi == "":  # 只有suci, 查看是否存在当前suci，若不存在就插入suci
            # if not suci in suci_map.keys():# 不存在当前suci
            insert_without_condition("transfer", "suci", suci)
            suci_map[suci] = True
            update_with_condition("transfer", "stage",str(stage_info(info_dict,concat_url)), "suci", suci)
        elif suci != "" and imsi != "":  # 同时有suci和imsi：建立对应关系, 查看是否存在suci，若存在，则更新对应的imsi(可能需要告警)
            if suci in suci_map.keys():  # suci必须存在
                insert_with_condition("transfer", "imsi", imsi, "suci", suci)
                imsi_map[imsi] = True
            update_with_condition("transfer", "stage",str(stage_info(info_dict,concat_url)), "suci",suci)
        elif suci == "" and imsi != "" and urnuuid == "":  # 只有imsi, 查看是否存在imsi，不存在则插入(可能需要告警)
            if imsi.count("-") == 2:
                imsi_list = imsi.split("-")
                imsi = imsi_list[0] + "-" + imsi_list[1]

            if not imsi in imsi_map.keys():  # imsi不可以不存在
                print("error 1")
                print(imsi)
            update_with_condition("transfer", "stage",str(stage_info(info_dict,concat_url)), "imsi",imsi)
        elif suci == "" and imsi != "" and urnuuid != "":  # 同时有imsi和urnuuid:建立对应关系，插入urn: uuid
            if imsi in imsi_map.keys():  # imsi必须存在
                insert_with_condition("transfer", "urnuuid", urnuuid, "imsi", imsi)
                urnuuid_map[urnuuid] = True
            update_with_condition("transfer", "stage",str(stage_info(info_dict,concat_url)), "imsi",imsi)
        elif suci == "" and imsi == "" and urnuuid != "":  # 只有urn:uuid->此时urn: uuid不能为空，查看是否存在urn: uuid(不存在需要告警)
            if not urnuuid in urnuuid_map.keys():
                print("error 2")
            update_with_condition("transfer", "stage",str(stage_info(info_dict,concat_url)), "urnuuid",urnuuid)
        return "ok"



if __name__ == '__main__':
    handler = UEfeatureHandler()

    processor = UEfeature.Processor(handler)
    transport = TSocket.TServerSocket(__HOST, __PORT)
    # 传输方式，使用buffer
    tfactory = TTransport.TBufferedTransportFactory()
    # 传输的数据类型：二进制
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # 创建一个thrift 服务
    rpcServer = TServer.TSimpleServer(processor,transport, tfactory, pfactory)

    print('Starting the rpc server at', __HOST,':', __PORT)
    rpcServer.serve()
    print('done')

