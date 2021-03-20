#统计过程中出现的服务端数量
#用于调用sklearn的相关模块对每一条流量做预测
#用于对预测结果进行投票统计，可以维护一个大的list
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn import svm

MIN=10#这段时间内出现的最小次数

def sklearn_predict(tcp_feature):
    """
    tcp_feature:提供的tcp特征
    这部分主要根据提供的tcp特征，返回对应的sklearn预测结果,一个list

    问题：标准化存在问题
    """
    sc = StandardScaler()
    sc.fit(tcp_feature)
    X_std = sc.transform(tcp_feature)

    #加载svm分类器
    f=open('svm.model','rb')
    model=pickle.loads(f.read())

    #计算结果并返回
    return model.predict(X_std)


def statistic(nf_ip,result):#统计预测结果中的ip:port与result的对应关系
    """
    nf_ip:预测的服务ip:port信息
    result：预测的结果

    返回nf_result字典信息
    """
    nf_result={}
    for itemA,itemB in zip(nf_ip,result):
        if itemA not in nf_result.keys():
            nf_result[itemA]=[itemB]
        else:
            nf_result[itemA].append(itemB)
    return nf_result

def vote(nf_result,nf_dict):#对多次结果进行投票，建议一次传过来两分钟的数据(每个网元12条)，进行投票
    """
    nf_result:传入的字典，内容为{"ip:port":[1,1,1,...,1],....},即一个ip:端口对在12次投票过程中的结果
    nf_dict:传入的字典，即已知的ip:port对应的网元ID/名称
    投票算法简单设计为对每一个ip:port对，计算出现次数最多的nf_id次数，如果超过9次就算做新网元

    问题：没有考虑如果网元端口提供的服务发生改变的情况
    """
    for item in nf_result.keys():
        if item not in nf_dict.keys():
            #统计item对应list的最大元素个数
            max_ele=max(nf_result[item],key=nf_result[item].count)
            max_ele_num=nf_result[item].count(max(nf_result[item],key=nf_result[item].count))
            if max_ele_num*1.0/len(nf_result[item])>=0.8 and len(nf_result[item])>=MIN:
                nf_dict[item]=max_ele
    return nf_dict