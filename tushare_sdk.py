import tushare as ts

# 设置token
ts.set_token('21c35e10dbac293e2535e61107b7777e83de449e088f6186fe888486')

# 初始化pro接口
pro = ts.pro_api()

df = pro.moneyflow_ths(ts_code='000417.SZ', start_date='20250101', end_date='20251219')

print(df)
