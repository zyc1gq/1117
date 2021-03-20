import sys
from UEfeatureService.ttypes import *
from UEfeatureService.constants import *
from UEfeatureService import UEfeature
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import json
import UE_feature
transport = TSocket.TSocket('localhost', 9000)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = UEfeature.Client(protocol)
# Connect!
transport.open()
#
# cmd = 2
# token = '1111-2222-3333-4444'
# data = json.dumps({"name":"zhoujielun"})
# msg = client.invoke(cmd,token,data)
# print(msg)
# transport.close()


def UEinvoke():
    result=UE_feature.link_mysql_geturl()
    msg=client.do_format(result[0])
    print(msg)

UEinvoke()
transport.close()