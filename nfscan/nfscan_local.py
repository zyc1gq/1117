import json
import numpy as np
import nf_utils

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from nfscanService import nfscan
from nfscanService import ttypes

from nfscanService import constants

__HOST = 'localhost'
__PORT = 9001

nf_dict = {}
class nfscanHandler:

    def predict(self,info_string):
        global nf_dict
        """
        info_list是info_string反序列化之后的结果，格式为：max,min,ave,tcpnumsize,ip:port
        """
        info_list=json.loads(info_string)
        info_list=np.array(info_list)

        #获取ip:port与tcp_feature信息
        ip_info=info_list[:,-1]
        tcp_feature=info_list[:,:-1]

        #进行预测
        result=nf_utils.sklearn_predict(tcp_feature)

        #统计对应关系
        nf_result=nf_utils.statistic(nf_ip=ip_info,result=result)

        #进行投票
        nf_dict=nf_utils.vote(nf_result,nf_dict)
        return "ok"

if __name__ == '__main__':
    handler = nfscanHandler()

    processor = nfscan.Processor(handler)
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

