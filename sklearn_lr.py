#使用max,min等时间统计特征做分类测试
#需要重新做数据统计,使用逻辑回归
#单纯的统计特征可能无法应对扩缩容之类问题，流量波峰(等比增加，归一化可以解决)可以应对
import pandas as pd
import numpy as np
import pymysql
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from sklearn import linear_model, datasets

connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='5gc',
                                     charset='utf8mb4')

def get_data():#获取mysql中的数据，并打乱
    #获取mysql中数据
    label_list=[]
    data_X=[]
    cursor = connection.cursor()
    for label in range(9):
        # 使用 execute()  方法执行 SQL 查询
        cursor.execute(
            "SELECT max,min,ave,tcpnumsize,nfID from tcp_stat_sx where nfID = "+str(label))

        # 使用 fetchone() 方法获取单条数据.s
        data = cursor.fetchall()
        res = np.array(data)
        for item in res:
            data_X.append(item[:-1])
            label_list.append(item[-1])

    return np.array(data_X),np.array(label_list)

def lr(X,Y):
    print(len(X))
    # 2.拆分测试集、训练集。
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=1)
    # 设置随机数种子，以便比较结果。

    # 3.标准化特征值
    sc = StandardScaler()
    sc.fit(X_train)
    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)

    # 4. 训练逻辑回归模型
    logreg = linear_model.LogisticRegression(C=5, penalty='l1', tol=0.01)
    logreg.fit(X_train_std, Y_train)

    # 5. 预测
    acc = logreg.score(X_train_std, Y_train)
    print(acc)
    acc = logreg.score(X_test_std, Y_test)
    print(acc)
    print(accuracy_score(Y_test,logreg.predict(X_test_std)))
X,Y=get_data()
lr(X,Y)
