import random
import math
import threading
import datetime
from bittrex.bittrex import Bittrex
import pandas as pd
from flask import Flask,render_template,request,json,redirect
from flaskext.mysql import MySQL
class CrptoClass:
    currencies = []

    app = Flask(__name__)
    mysql = MySQL()
    global mb
    _username=''
    #data members declarations.
    max_buy = 0.1
    min_buy = 0.01
    safe_cap_multiplier = 1.1
    margin = 1.015
    simulation = 1
    price = 0.056
    counter = 0
    currencyPairs=[]
    prices={}
    last_bought={}
    buy_caps={}
    state={}
    trades=[]
    period = 10
    out=0
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = ''
    app.config['MYSQL_DATABASE_DB'] = 'bucketlist'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    mysql.init_app(app)
    conn = mysql.connect()
    cursor = conn.cursor()
    #pair = "BTC-ETH"

    # noinspection PyArgumentList
    def __init__(self):
        period=10
        self.mb = Bittrex(None, None)
        for i in self.currencies:
            pair='BTC-'+i
            self.state[pair]="neutral"
            self.last_bought[pair] = {}
            self.last_bought[pair]['price'] = 0
            self.last_bought[pair]['amount'] = 0
            if(self.mb.get_market_summary(pair)['result'][0]['BaseVolume']>50):
                print("Base Volume is : ",self.mb.get_market_summary(pair)['result'][0]['BaseVolume'])
            #wee have pushed currency pair and their max_buys
                self.currencyPairs.append(pair)
                self.prices[pair]=[]
                self.buy_caps[pair] =round((self.safe_cap_multiplier*(self.mb.get_market_summary(pair)['result'][0]['Last'])),4)
        # Printing pairs ad=nd max_buys
            print("Currency Pairs : ",self.currencyPairs)
            print("Max Buys for Pairs :",self.buy_caps)
            print("Prices List : ",self.prices)
            print("Initial state ",self.state)
        print()
        print()



    def set_interval(self,func, sec):
        def func_wrapper():
            self.set_interval(func, sec)
            func()

        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def change(self):
        self.counter = self.counter + 1
        self.price = round(self.price - 0.001,4)
        for i in self.currencyPairs:
            list=[self.counter,self.price]
            self.prices[i].append(list)
            length = len(self.prices[i])
            #print("length is ", length)
            #print("Prices dictionary ---->", self.prices)
            if length > 1:
                print("Enter in update tangent")
                self.updateTangentAngles(i)
                print("")







    def returnTicker(self):
        #print("*****welcome To ticker event*****")
        for i in self.currencies:
            pair='BTC-'+i
            price=round(self.mb.get_ticker(pair)['result']['Last'],4)
            counter=len(self.prices[pair])
            #print("counter value is :",counter)
            list = [counter, price]
            if counter==0:
                print("c1:", counter)
                self.prices[pair].append(list)
            if self.prices[pair][counter-1][1]!=price:
                print("c2:",counter)
                self.prices[pair].append(list)
            if len(self.prices[pair])>1:
                print("Going to update tangent")
                self.updateTangentAngles(pair)

            print("Current states ",self.state)
            print("Current Prices list is :",self.prices)
            print()
            print()

    def updateTangentAngles(self,pair):
        print("pair is :",pair)
        #print("In update tangent angle")
        Number_Of_Lists=len(self.prices[pair])
        print("total tuples for the list :",Number_Of_Lists)
        Tuple1=self.prices[pair][Number_Of_Lists-2]
        Tuple2=self.prices[pair][Number_Of_Lists-1]
        print("Tuple 1 : ",Tuple1,"  Tuple  2 : ",Tuple2)
        price1=Tuple1[1]
        price2=Tuple2[1]
        Curr_Price=price2
        diff = round(price2 - price1, 4)
        #print("Difference in Y :", diff)
        Ang = (math.atan2(diff, 1) * 180) / math.pi
        print("Angle is :", Ang)

        if(self.state[pair]=="dropping" and Ang>0):
            #print("**Dropping and Angle Greater than 0**")
            if(self.last_bought[pair]['price']==0 and Curr_Price<self.buy_caps[pair]):
                print("Going to Place Order Buy")
                self.placeOrder(pair,"BUY",Curr_Price,self.max_buy)

        if(self.state[pair]=="rising" and Ang<0):
            #print("**rising and Angle Less than 0**")
            if(self.last_bought[pair]['price']!=0 and Curr_Price>self.last_bought[pair]['price']):
                print("Going to Place Order Sell")
                print("**rising and Angle Less than 0**")
                self.placeOrder(pair, "SELL", Curr_Price,self.max_buy)

        if (Ang < 0):
            #print("First negative")
            self.state[pair] = "dropping"
            #print(self.state)
        if (Ang > 0):
            #print("First positive")
            self.state[pair] = "rising"
    def updateCsv(self):

        df=pd.DataFrame(self.trades,columns=['Pair', 'Type', 'Rate', 'Amount', 'Amount(BTC)', 'Time', 'Margin'])
        df.to_csv("C:\\Users\\user\\Desktop\\trades.csv",index=False)

    def placeOrder(self ,pair, Type, Rate,Max_Buy):
        amount=Max_Buy/Rate #this defines quantity of currency we will buy
        print("amount bought",amount)
        amt_btc=0.1
        margin=0
        if(Type == "BUY"):
            print("In Buy Section")
            if(self.simulation):

                self.last_bought[pair]['price'] = Rate
                self.last_bought[pair]['amount'] = amount
                amt_btc = round(Rate * amount, 4)
                print(self.last_bought)
                self.trades.append({'Pair':pair,'Type':Type,'Rate':Rate,'Amount':amount,
                                    'Amount(BTC)':amt_btc,'Time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                #print("Buy trade",self.trades)

        elif(Type == "SELL"):

            print("In Sell Section")
            Rate=Rate*0.999
            amount=self.last_bought[pair]['amount']*0.995
            amt_btc = round(Rate * amount, 4)
            margin=100*(Rate*amount - amount*self.last_bought[pair]['price'])/(amount*self.last_bought[pair]['price'])
            self.trades.append({'Pair': pair, 'Type': Type, 'Rate': Rate, 'Amount': amount,
                              'Amount(BTC)': amt_btc,
                                'Time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'Margin':margin})
            #print("sell trades",self.trades)

            print("Margin is :",margin)
            self.prices[pair]=[]
            self.state[pair]="neutral"
            self.last_bought[pair] = {}
            self.last_bought[pair]['price'] = 0
            self.last_bought[pair]['amount'] = 0
            print("State after selling ",self.state[pair])
            print("Price list gets empty ",self.prices[pair])

            print()
        self.updateCsv()
        print('user: ',self._username)
        self.cursor.callproc('sp_startTrade', (self._username,pair,Type,Rate,amount,amt_btc,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),margin))
        # query = "INSERT INTO trades(user_username,Pair,Type,Rate,Amount,Amount(BTC),Time,Margin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
        # # val=(self._username,pair,Type,Rate,amount,amt_btc,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),margin)
        # val = (self._username, 'pair', 'Type', 'Rate', 'amount','amt_btc', 'datetime','margin')
        # self.cursor.execute(query, val)
        # self.updateCsv()

    def randomGen(self):
        x = random.uniform(float(-1), float(1))
        print("random number generated is : ", x)
        return x



#A=Mosbot()
# A.returnTicker()
# A.returnTicker()
# A.returnTicker()
# A.returnTicker()
# A.returnTicker()
# A.returnTicker()
#A.placeOrder("er","BUY",34,65)
#A.set_interval(A.returnTicker,7)
