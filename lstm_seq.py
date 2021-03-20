#使用lstm做序列分类->尝试
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout, Bidirectional
from keras.optimizers import Adam
import pymysql
from dateutil.parser import parse
import datetime
from keras.models import load_model
connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='5gc',
                                     charset='utf8mb4')
def create_model():
    model = Sequential()
    model.add(Bidirectional(LSTM(units=256, dropout=0.5, input_shape=(None, 7), return_sequences=True)))
    model.add(Bidirectional(LSTM(units=128, dropout=0.5)))
    model.add(Dense(units=8, activation="softmax"))
    model.compile(loss="mse", optimizer="adam", metrics=["accuracy"])
    return model

def train_model(data_all,label_list):
    model=create_model()
    model.fit(data_all,label_list,batch_size=32,epochs=20,validation_split=0.2,shuffle=True)



def get_data():#获取mysql中的数据，并打乱
    #获取mysql中数据
    label_list=[]
    data_X=[]
    cursor = connection.cursor()
    for label in range(8):
        # 使用 execute()  方法执行 SQL 查询
        cursor.execute(
            "SELECT max,min,ave,fc,num,allnum,tcpnum,nfID from tcp_stat2 where nfID = "+str(label))

        # 使用 fetchone() 方法获取单条数据.s
        data = cursor.fetchall()
        res = np.array(data)
        for item in res:
            data_X.append([item[:-1]])
            label_list.append(item[-1])

    return np.array(data_X),np.array(label_list)

A,B=get_data()
A=A.astype(float)
print(A.shape)
train_model(A,B)
