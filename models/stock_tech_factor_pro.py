from sqlalchemy import Column, BigInteger, String, DECIMAL, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

class StockTechFactorPro(Base):
    """股票技术面因子专业版模型 - 基于stk_factor_pro接口"""
    __tablename__ = 'stock_tech_factor_pro'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    
    # 基础行情数据
    open = Column(DECIMAL(20, 10), comment='开盘价')
    open_hfq = Column(DECIMAL(20, 10), comment='开盘价（后复权）')
    open_qfq = Column(DECIMAL(20, 10), comment='开盘价（前复权）')
    high = Column(DECIMAL(20, 10), comment='最高价')
    high_hfq = Column(DECIMAL(20, 10), comment='最高价（后复权）')
    high_qfq = Column(DECIMAL(20, 10), comment='最高价（前复权）')
    low = Column(DECIMAL(20, 10), comment='最低价')
    low_hfq = Column(DECIMAL(20, 10), comment='最低价（后复权）')
    low_qfq = Column(DECIMAL(20, 10), comment='最低价（前复权）')
    close = Column(DECIMAL(20, 10), comment='收盘价')
    close_hfq = Column(DECIMAL(20, 10), comment='收盘价（后复权）')
    close_qfq = Column(DECIMAL(20, 10), comment='收盘价（前复权）')
    pre_close = Column(DECIMAL(20, 10), comment='昨收价(前复权)')
    change = Column(DECIMAL(20, 10), comment='涨跌额')
    pct_chg = Column(DECIMAL(20, 10), comment='涨跌幅')
    vol = Column(DECIMAL(20, 10), comment='成交量（手）')
    amount = Column(DECIMAL(20, 10), comment='成交额（千元）')
    
    # 市场指标
    turnover_rate = Column(DECIMAL(20, 10), comment='换手率（%）')
    turnover_rate_f = Column(DECIMAL(20, 10), comment='换手率（自由流通股）')
    volume_ratio = Column(DECIMAL(20, 10), comment='量比')
    pe = Column(DECIMAL(20, 10), comment='市盈率')
    pe_ttm = Column(DECIMAL(20, 10), comment='市盈率（TTM）')
    pb = Column(DECIMAL(20, 10), comment='市净率')
    ps = Column(DECIMAL(20, 10), comment='市销率')
    ps_ttm = Column(DECIMAL(20, 10), comment='市销率（TTM）')
    dv_ratio = Column(DECIMAL(20, 10), comment='股息率（%）')
    dv_ttm = Column(DECIMAL(20, 10), comment='股息率（TTM）（%）')
    total_share = Column(DECIMAL(20, 10), comment='总股本（万股）')
    float_share = Column(DECIMAL(20, 10), comment='流通股本（万股）')
    free_share = Column(DECIMAL(20, 10), comment='自由流通股本（万）')
    total_mv = Column(DECIMAL(20, 10), comment='总市值（万元）')
    circ_mv = Column(DECIMAL(20, 10), comment='流通市值（万元）')
    adj_factor = Column(DECIMAL(20, 10), comment='复权因子')
    
    # 连涨连跌天数
    downdays = Column(DECIMAL(20, 10), comment='连跌天数')
    updays = Column(DECIMAL(20, 10), comment='连涨天数')
    lowdays = Column(DECIMAL(20, 10), comment='最低价周期')
    topdays = Column(DECIMAL(20, 10), comment='最高价周期')
    
    # ASI振动升降指标
    asi_bfq = Column(DECIMAL(20, 10), comment='ASI不复权')
    asi_hfq = Column(DECIMAL(20, 10), comment='ASI后复权')
    asi_qfq = Column(DECIMAL(20, 10), comment='ASI前复权')
    asit_bfq = Column(DECIMAL(20, 10), comment='ASIT不复权')
    asit_hfq = Column(DECIMAL(20, 10), comment='ASIT后复权')
    asit_qfq = Column(DECIMAL(20, 10), comment='ASIT前复权')
    
    # ATR真实波动
    atr_bfq = Column(DECIMAL(20, 10), comment='ATR不复权')
    atr_hfq = Column(DECIMAL(20, 10), comment='ATR后复权')
    atr_qfq = Column(DECIMAL(20, 10), comment='ATR前复权')
    
    # BBI多空指标
    bbi_bfq = Column(DECIMAL(20, 10), comment='BBI不复权')
    bbi_hfq = Column(DECIMAL(20, 10), comment='BBI后复权')
    bbi_qfq = Column(DECIMAL(20, 10), comment='BBI前复权')
    
    # BIAS乖离率
    bias1_bfq = Column(DECIMAL(20, 10), comment='BIAS1不复权')
    bias1_hfq = Column(DECIMAL(20, 10), comment='BIAS1后复权')
    bias1_qfq = Column(DECIMAL(20, 10), comment='BIAS1前复权')
    bias2_bfq = Column(DECIMAL(20, 10), comment='BIAS2不复权')
    bias2_hfq = Column(DECIMAL(20, 10), comment='BIAS2后复权')
    bias2_qfq = Column(DECIMAL(20, 10), comment='BIAS2前复权')
    bias3_bfq = Column(DECIMAL(20, 10), comment='BIAS3不复权')
    bias3_hfq = Column(DECIMAL(20, 10), comment='BIAS3后复权')
    bias3_qfq = Column(DECIMAL(20, 10), comment='BIAS3前复权')
    
    # BOLL布林带
    boll_lower_bfq = Column(DECIMAL(20, 10), comment='BOLL下轨不复权')
    boll_lower_hfq = Column(DECIMAL(20, 10), comment='BOLL下轨后复权')
    boll_lower_qfq = Column(DECIMAL(20, 10), comment='BOLL下轨前复权')
    boll_mid_bfq = Column(DECIMAL(20, 10), comment='BOLL中轨不复权')
    boll_mid_hfq = Column(DECIMAL(20, 10), comment='BOLL中轨后复权')
    boll_mid_qfq = Column(DECIMAL(20, 10), comment='BOLL中轨前复权')
    boll_upper_bfq = Column(DECIMAL(20, 10), comment='BOLL上轨不复权')
    boll_upper_hfq = Column(DECIMAL(20, 10), comment='BOLL上轨后复权')
    boll_upper_qfq = Column(DECIMAL(20, 10), comment='BOLL上轨前复权')
    
    # BRAR情绪指标
    brar_ar_bfq = Column(DECIMAL(20, 10), comment='BRAR_AR不复权')
    brar_ar_hfq = Column(DECIMAL(20, 10), comment='BRAR_AR后复权')
    brar_ar_qfq = Column(DECIMAL(20, 10), comment='BRAR_AR前复权')
    brar_br_bfq = Column(DECIMAL(20, 10), comment='BRAR_BR不复权')
    brar_br_hfq = Column(DECIMAL(20, 10), comment='BRAR_BR后复权')
    brar_br_qfq = Column(DECIMAL(20, 10), comment='BRAR_BR前复权')
    
    # CCI顺势指标
    cci_bfq = Column(DECIMAL(20, 10), comment='CCI不复权')
    cci_hfq = Column(DECIMAL(20, 10), comment='CCI后复权')
    cci_qfq = Column(DECIMAL(20, 10), comment='CCI前复权')
    
    # CR价格动量指标
    cr_bfq = Column(DECIMAL(20, 10), comment='CR不复权')
    cr_hfq = Column(DECIMAL(20, 10), comment='CR后复权')
    cr_qfq = Column(DECIMAL(20, 10), comment='CR前复权')
    
    # DFMA平行线差指标
    dfma_dif_bfq = Column(DECIMAL(20, 10), comment='DFMA_DIF不复权')
    dfma_dif_hfq = Column(DECIMAL(20, 10), comment='DFMA_DIF后复权')
    dfma_dif_qfq = Column(DECIMAL(20, 10), comment='DFMA_DIF前复权')
    dfma_difma_bfq = Column(DECIMAL(20, 10), comment='DFMA_DIFMA不复权')
    dfma_difma_hfq = Column(DECIMAL(20, 10), comment='DFMA_DIFMA后复权')
    dfma_difma_qfq = Column(DECIMAL(20, 10), comment='DFMA_DIFMA前复权')
    
    # DMI动向指标
    dmi_adx_bfq = Column(DECIMAL(20, 10), comment='DMI_ADX不复权')
    dmi_adx_hfq = Column(DECIMAL(20, 10), comment='DMI_ADX后复权')
    dmi_adx_qfq = Column(DECIMAL(20, 10), comment='DMI_ADX前复权')
    dmi_adxr_bfq = Column(DECIMAL(20, 10), comment='DMI_ADXR不复权')
    dmi_adxr_hfq = Column(DECIMAL(20, 10), comment='DMI_ADXR后复权')
    dmi_adxr_qfq = Column(DECIMAL(20, 10), comment='DMI_ADXR前复权')
    dmi_mdi_bfq = Column(DECIMAL(20, 10), comment='DMI_MDI不复权')
    dmi_mdi_hfq = Column(DECIMAL(20, 10), comment='DMI_MDI后复权')
    dmi_mdi_qfq = Column(DECIMAL(20, 10), comment='DMI_MDI前复权')
    dmi_pdi_bfq = Column(DECIMAL(20, 10), comment='DMI_PDI不复权')
    dmi_pdi_hfq = Column(DECIMAL(20, 10), comment='DMI_PDI后复权')
    dmi_pdi_qfq = Column(DECIMAL(20, 10), comment='DMI_PDI前复权')
    
    # DPO区间震荡线
    dpo_bfq = Column(DECIMAL(20, 10), comment='DPO不复权')
    dpo_hfq = Column(DECIMAL(20, 10), comment='DPO后复权')
    dpo_qfq = Column(DECIMAL(20, 10), comment='DPO前复权')
    madpo_bfq = Column(DECIMAL(20, 10), comment='MADPO不复权')
    madpo_hfq = Column(DECIMAL(20, 10), comment='MADPO后复权')
    madpo_qfq = Column(DECIMAL(20, 10), comment='MADPO前复权')
    
    # EMA指数移动平均
    ema_bfq_5 = Column(DECIMAL(20, 10), comment='EMA5不复权')
    ema_bfq_10 = Column(DECIMAL(20, 10), comment='EMA10不复权')
    ema_bfq_20 = Column(DECIMAL(20, 10), comment='EMA20不复权')
    ema_bfq_30 = Column(DECIMAL(20, 10), comment='EMA30不复权')
    ema_bfq_60 = Column(DECIMAL(20, 10), comment='EMA60不复权')
    ema_bfq_90 = Column(DECIMAL(20, 10), comment='EMA90不复权')
    ema_bfq_250 = Column(DECIMAL(20, 10), comment='EMA250不复权')
    ema_hfq_5 = Column(DECIMAL(20, 10), comment='EMA5后复权')
    ema_hfq_10 = Column(DECIMAL(20, 10), comment='EMA10后复权')
    ema_hfq_20 = Column(DECIMAL(20, 10), comment='EMA20后复权')
    ema_hfq_30 = Column(DECIMAL(20, 10), comment='EMA30后复权')
    ema_hfq_60 = Column(DECIMAL(20, 10), comment='EMA60后复权')
    ema_hfq_90 = Column(DECIMAL(20, 10), comment='EMA90后复权')
    ema_hfq_250 = Column(DECIMAL(20, 10), comment='EMA250后复权')
    ema_qfq_5 = Column(DECIMAL(20, 10), comment='EMA5前复权')
    ema_qfq_10 = Column(DECIMAL(20, 10), comment='EMA10前复权')
    ema_qfq_20 = Column(DECIMAL(20, 10), comment='EMA20前复权')
    ema_qfq_30 = Column(DECIMAL(20, 10), comment='EMA30前复权')
    ema_qfq_60 = Column(DECIMAL(20, 10), comment='EMA60前复权')
    ema_qfq_90 = Column(DECIMAL(20, 10), comment='EMA90前复权')
    ema_qfq_250 = Column(DECIMAL(20, 10), comment='EMA250前复权')
    
    # EMV简易波动指标
    emv_bfq = Column(DECIMAL(20, 10), comment='EMV不复权')
    emv_hfq = Column(DECIMAL(20, 10), comment='EMV后复权')
    emv_qfq = Column(DECIMAL(20, 10), comment='EMV前复权')
    maemv_bfq = Column(DECIMAL(20, 10), comment='MAEMV不复权')
    maemv_hfq = Column(DECIMAL(20, 10), comment='MAEMV后复权')
    maemv_qfq = Column(DECIMAL(20, 10), comment='MAEMV前复权')
    
    # EXPMA指数平均数
    expma_12_bfq = Column(DECIMAL(20, 10), comment='EXPMA12不复权')
    expma_12_hfq = Column(DECIMAL(20, 10), comment='EXPMA12后复权')
    expma_12_qfq = Column(DECIMAL(20, 10), comment='EXPMA12前复权')
    expma_50_bfq = Column(DECIMAL(20, 10), comment='EXPMA50不复权')
    expma_50_hfq = Column(DECIMAL(20, 10), comment='EXPMA50后复权')
    expma_50_qfq = Column(DECIMAL(20, 10), comment='EXPMA50前复权')
    
    # KDJ指标
    kdj_bfq = Column(DECIMAL(20, 10), comment='KDJ_J不复权')
    kdj_hfq = Column(DECIMAL(20, 10), comment='KDJ_J后复权')
    kdj_qfq = Column(DECIMAL(20, 10), comment='KDJ_J前复权')
    kdj_d_bfq = Column(DECIMAL(20, 10), comment='KDJ_D不复权')
    kdj_d_hfq = Column(DECIMAL(20, 10), comment='KDJ_D后复权')
    kdj_d_qfq = Column(DECIMAL(20, 10), comment='KDJ_D前复权')
    kdj_k_bfq = Column(DECIMAL(20, 10), comment='KDJ_K不复权')
    kdj_k_hfq = Column(DECIMAL(20, 10), comment='KDJ_K后复权')
    kdj_k_qfq = Column(DECIMAL(20, 10), comment='KDJ_K前复权')
    
    # KTN肯特纳交易通道
    ktn_down_bfq = Column(DECIMAL(20, 10), comment='KTN下轨不复权')
    ktn_down_hfq = Column(DECIMAL(20, 10), comment='KTN下轨后复权')
    ktn_down_qfq = Column(DECIMAL(20, 10), comment='KTN下轨前复权')
    ktn_mid_bfq = Column(DECIMAL(20, 10), comment='KTN中轨不复权')
    ktn_mid_hfq = Column(DECIMAL(20, 10), comment='KTN中轨后复权')
    ktn_mid_qfq = Column(DECIMAL(20, 10), comment='KTN中轨前复权')
    ktn_upper_bfq = Column(DECIMAL(20, 10), comment='KTN上轨不复权')
    ktn_upper_hfq = Column(DECIMAL(20, 10), comment='KTN上轨后复权')
    ktn_upper_qfq = Column(DECIMAL(20, 10), comment='KTN上轨前复权')
    
    # MA简单移动平均
    ma_bfq_5 = Column(DECIMAL(20, 10), comment='MA5不复权')
    ma_bfq_10 = Column(DECIMAL(20, 10), comment='MA10不复权')
    ma_bfq_20 = Column(DECIMAL(20, 10), comment='MA20不复权')
    ma_bfq_30 = Column(DECIMAL(20, 10), comment='MA30不复权')
    ma_bfq_60 = Column(DECIMAL(20, 10), comment='MA60不复权')
    ma_bfq_90 = Column(DECIMAL(20, 10), comment='MA90不复权')
    ma_bfq_250 = Column(DECIMAL(20, 10), comment='MA250不复权')
    ma_hfq_5 = Column(DECIMAL(20, 10), comment='MA5后复权')
    ma_hfq_10 = Column(DECIMAL(20, 10), comment='MA10后复权')
    ma_hfq_20 = Column(DECIMAL(20, 10), comment='MA20后复权')
    ma_hfq_30 = Column(DECIMAL(20, 10), comment='MA30后复权')
    ma_hfq_60 = Column(DECIMAL(20, 10), comment='MA60后复权')
    ma_hfq_90 = Column(DECIMAL(20, 10), comment='MA90后复权')
    ma_hfq_250 = Column(DECIMAL(20, 10), comment='MA250后复权')
    ma_qfq_5 = Column(DECIMAL(20, 10), comment='MA5前复权')
    ma_qfq_10 = Column(DECIMAL(20, 10), comment='MA10前复权')
    ma_qfq_20 = Column(DECIMAL(20, 10), comment='MA20前复权')
    ma_qfq_30 = Column(DECIMAL(20, 10), comment='MA30前复权')
    ma_qfq_60 = Column(DECIMAL(20, 10), comment='MA60前复权')
    ma_qfq_90 = Column(DECIMAL(20, 10), comment='MA90前复权')
    ma_qfq_250 = Column(DECIMAL(20, 10), comment='MA250前复权')
    
    # MACD指标
    macd_bfq = Column(DECIMAL(20, 10), comment='MACD不复权')
    macd_hfq = Column(DECIMAL(20, 10), comment='MACD后复权')
    macd_qfq = Column(DECIMAL(20, 10), comment='MACD前复权')
    macd_dea_bfq = Column(DECIMAL(20, 10), comment='MACD_DEA不复权')
    macd_dea_hfq = Column(DECIMAL(20, 10), comment='MACD_DEA后复权')
    macd_dea_qfq = Column(DECIMAL(20, 10), comment='MACD_DEA前复权')
    macd_dif_bfq = Column(DECIMAL(20, 10), comment='MACD_DIF不复权')
    macd_dif_hfq = Column(DECIMAL(20, 10), comment='MACD_DIF后复权')
    macd_dif_qfq = Column(DECIMAL(20, 10), comment='MACD_DIF前复权')
    
    # MASS梅斯线
    mass_bfq = Column(DECIMAL(20, 10), comment='MASS不复权')
    mass_hfq = Column(DECIMAL(20, 10), comment='MASS后复权')
    mass_qfq = Column(DECIMAL(20, 10), comment='MASS前复权')
    ma_mass_bfq = Column(DECIMAL(20, 10), comment='MA_MASS不复权')
    ma_mass_hfq = Column(DECIMAL(20, 10), comment='MA_MASS后复权')
    ma_mass_qfq = Column(DECIMAL(20, 10), comment='MA_MASS前复权')
    
    # MFI指标
    mfi_bfq = Column(DECIMAL(20, 10), comment='MFI不复权')
    mfi_hfq = Column(DECIMAL(20, 10), comment='MFI后复权')
    mfi_qfq = Column(DECIMAL(20, 10), comment='MFI前复权')
    
    # MTM动量指标
    mtm_bfq = Column(DECIMAL(20, 10), comment='MTM不复权')
    mtm_hfq = Column(DECIMAL(20, 10), comment='MTM后复权')
    mtm_qfq = Column(DECIMAL(20, 10), comment='MTM前复权')
    mtmma_bfq = Column(DECIMAL(20, 10), comment='MTMMA不复权')
    mtmma_hfq = Column(DECIMAL(20, 10), comment='MTMMA后复权')
    mtmma_qfq = Column(DECIMAL(20, 10), comment='MTMMA前复权')
    
    # OBV能量潮指标
    obv_bfq = Column(DECIMAL(20, 10), comment='OBV不复权')
    obv_hfq = Column(DECIMAL(20, 10), comment='OBV后复权')
    obv_qfq = Column(DECIMAL(20, 10), comment='OBV前复权')
    
    # PSY心理线指标
    psy_bfq = Column(DECIMAL(20, 10), comment='PSY不复权')
    psy_hfq = Column(DECIMAL(20, 10), comment='PSY后复权')
    psy_qfq = Column(DECIMAL(20, 10), comment='PSY前复权')
    psyma_bfq = Column(DECIMAL(20, 10), comment='PSYMA不复权')
    psyma_hfq = Column(DECIMAL(20, 10), comment='PSYMA后复权')
    psyma_qfq = Column(DECIMAL(20, 10), comment='PSYMA前复权')
    
    # ROC变动率指标
    roc_bfq = Column(DECIMAL(20, 10), comment='ROC不复权')
    roc_hfq = Column(DECIMAL(20, 10), comment='ROC后复权')
    roc_qfq = Column(DECIMAL(20, 10), comment='ROC前复权')
    maroc_bfq = Column(DECIMAL(20, 10), comment='MAROC不复权')
    maroc_hfq = Column(DECIMAL(20, 10), comment='MAROC后复权')
    maroc_qfq = Column(DECIMAL(20, 10), comment='MAROC前复权')
    
    # RSI指标
    rsi_bfq_6 = Column(DECIMAL(20, 10), comment='RSI6不复权')
    rsi_bfq_12 = Column(DECIMAL(20, 10), comment='RSI12不复权')
    rsi_bfq_24 = Column(DECIMAL(20, 10), comment='RSI24不复权')
    rsi_hfq_6 = Column(DECIMAL(20, 10), comment='RSI6后复权')
    rsi_hfq_12 = Column(DECIMAL(20, 10), comment='RSI12后复权')
    rsi_hfq_24 = Column(DECIMAL(20, 10), comment='RSI24后复权')
    rsi_qfq_6 = Column(DECIMAL(20, 10), comment='RSI6前复权')
    rsi_qfq_12 = Column(DECIMAL(20, 10), comment='RSI12前复权')
    rsi_qfq_24 = Column(DECIMAL(20, 10), comment='RSI24前复权')
    
    # TAQ唐安奇通道
    taq_down_bfq = Column(DECIMAL(20, 10), comment='TAQ下轨不复权')
    taq_down_hfq = Column(DECIMAL(20, 10), comment='TAQ下轨后复权')
    taq_down_qfq = Column(DECIMAL(20, 10), comment='TAQ下轨前复权')
    taq_mid_bfq = Column(DECIMAL(20, 10), comment='TAQ中轨不复权')
    taq_mid_hfq = Column(DECIMAL(20, 10), comment='TAQ中轨后复权')
    taq_mid_qfq = Column(DECIMAL(20, 10), comment='TAQ中轨前复权')
    taq_up_bfq = Column(DECIMAL(20, 10), comment='TAQ上轨不复权')
    taq_up_hfq = Column(DECIMAL(20, 10), comment='TAQ上轨后复权')
    taq_up_qfq = Column(DECIMAL(20, 10), comment='TAQ上轨前复权')
    
    # TRIX三重指数平滑平均线
    trix_bfq = Column(DECIMAL(20, 10), comment='TRIX不复权')
    trix_hfq = Column(DECIMAL(20, 10), comment='TRIX后复权')
    trix_qfq = Column(DECIMAL(20, 10), comment='TRIX前复权')
    trma_bfq = Column(DECIMAL(20, 10), comment='TRMA不复权')
    trma_hfq = Column(DECIMAL(20, 10), comment='TRMA后复权')
    trma_qfq = Column(DECIMAL(20, 10), comment='TRMA前复权')
    
    # VR容量比率
    vr_bfq = Column(DECIMAL(20, 10), comment='VR不复权')
    vr_hfq = Column(DECIMAL(20, 10), comment='VR后复权')
    vr_qfq = Column(DECIMAL(20, 10), comment='VR前复权')
    
    # WR威廉指标
    wr_bfq = Column(DECIMAL(20, 10), comment='WR不复权')
    wr_hfq = Column(DECIMAL(20, 10), comment='WR后复权')
    wr_qfq = Column(DECIMAL(20, 10), comment='WR前复权')
    wr1_bfq = Column(DECIMAL(20, 10), comment='WR1不复权')
    wr1_hfq = Column(DECIMAL(20, 10), comment='WR1后复权')
    wr1_qfq = Column(DECIMAL(20, 10), comment='WR1前复权')
    
    # XSII薛斯通道II
    xsii_td1_bfq = Column(DECIMAL(20, 10), comment='XSII_TD1不复权')
    xsii_td1_hfq = Column(DECIMAL(20, 10), comment='XSII_TD1后复权')
    xsii_td1_qfq = Column(DECIMAL(20, 10), comment='XSII_TD1前复权')
    xsii_td2_bfq = Column(DECIMAL(20, 10), comment='XSII_TD2不复权')
    xsii_td2_hfq = Column(DECIMAL(20, 10), comment='XSII_TD2后复权')
    xsii_td2_qfq = Column(DECIMAL(20, 10), comment='XSII_TD2前复权')
    xsii_td3_bfq = Column(DECIMAL(20, 10), comment='XSII_TD3不复权')
    xsii_td3_hfq = Column(DECIMAL(20, 10), comment='XSII_TD3后复权')
    xsii_td3_qfq = Column(DECIMAL(20, 10), comment='XSII_TD3前复权')
    xsii_td4_bfq = Column(DECIMAL(20, 10), comment='XSII_TD4不复权')
    xsii_td4_hfq = Column(DECIMAL(20, 10), comment='XSII_TD4后复权')
    xsii_td4_qfq = Column(DECIMAL(20, 10), comment='XSII_TD4前复权')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_tech_factor_pro'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )
