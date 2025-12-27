import tushare as ts  

def guess_number_game():
    pro = ts.pro_api('your token')

    df = pro.moneyflow(trade_date='20190315')
    print(df)

