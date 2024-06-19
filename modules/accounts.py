import re


def get_eating_account(payee, description, time=None):
    if time == None or not hasattr(time, 'hour'):
        return 'Expenses:Dining:Diet'
    elif time.hour <= 3 or time.hour >= 21:
        return 'Expenses:Eating:Nightingale'
    elif time.hour <= 10:
        return 'Expenses:Eating:Breakfast'
    elif time.hour <= 16:
        return 'Expenses:Eating:Lunch'
    else:
        return 'Expenses:Eating:Supper'


def get_credit_return(from_user, description, time=None):
    for key, value in credit_cards.items():
        if key == from_user:
            return value
    return "Unknown"


public_accounts = [
    'Assets:Company:Alipay:StupidAlipay'
]

credit_cards = {
    '中信银行': 'Liabilities:CreditCard:CITIC',
}

accounts = {
    "余额宝": 'Assets:Company:Alipay:MonetaryFund',
    '余利宝': 'Assets:Bank:MyBank',
    '花呗': 'Liabilities:Company:Huabei',
    '建设银行': 'Liabilities:CreditCard:CCB',
    '零钱': 'Assets:Balances:WeChat',
}

descriptions = {
    '余额宝.*收益发放': 'Assets:Company:Alipay:MonetaryFund',
    '转入到余利宝': 'Assets:Bank:MyBank',
    '花呗收钱服务费': 'Expenses:Fee',
    '自动还款-花呗.*账单': 'Liabilities:Company:Huabei',
    '信用卡自动还款|信用卡还款': get_credit_return,
    '外卖订单': get_eating_account,
    '美团订单': get_eating_account,
}

anothers = {
    '.*上海拉扎斯.*': get_eating_account,
    '.*伏沄.*|便电通.*|友宝|.*友宝昂莱.*': 'Expenses:Dining:Drink',
    '北京一卡通': 'Expenses:Traffic:Bus',
    '怂柠.*|茶话弄.*|沪上阿姨.*|吴裕泰.*|CoCo都可.*|星巴克.*|喜茶.*|蜜雪冰城.*': 'Expenses:Dining:Drink',
    '北京中燃天天然气': 'Expenses:Dining:Diet',
    '觀盛楼.*|.*汉堡王.*|.*肯德基.*|金拱门.*|鲜芋仙.*': 'Expenses:Dining:Diet',
    '.*麦当劳.*|.*西少爷.*|.*吉野家.*|.*宏状元.*|连姐肉饼.*|老街围炉麻辣烫.*': 'Expenses:Dining:Diet',
    '.*火锅鸡.*|高兴火锅.*|友仁居.*': 'Expenses:Dining:Feast',
    '欧尚.*|.*便利蜂.*|.*欧尚.*|.*鲜市吉.*|柒一拾壹.*|.*盒马.*|.*超市|好德百汇.*|上嘉超市.*|北京维果蔬农副产品.*|超市发.*|鲜又多果蔬连锁超市.*|生活便利超市.*|都市优选.*|快客.*': 'Expenses:Groceries',
    '.*博众云.*|.*哈啰.*|安心充.*|.*车充安.*|.*全来电.*|小绿人充电|上海哈啰.*': 'Expenses:Traffic:Bike',
    '.*话费充值.*': 'Expenses:Utilities:CellPhone',
    '铁道部.*|中铁网络.*|.*12306.*': 'Expenses:Traffic:Train',
    '北京自来水': 'Expenses:Utilities:Water',
    '网上国网|北京电力|沧州供电公司': 'Expenses:Utilities:Electricity',
    '.*顺丰.*': 'Expenses:Utilities:Express',
    '滴滴出行|滴滴出租车|滴滴打车|滴滴快车': 'Expenses:Traffic:Taxi',
    '.*迪卡侬.*|.*优衣库.*': 'Expenses:Clothing',
    '.*华住*': 'Expenses:Hotel',
}

incomes = {
    '余额宝.*收益发放': 'Income:Trade:PnL',
}

description_res = dict([(key, re.compile(key)) for key in descriptions])
another_res = dict([(key, re.compile(key)) for key in anothers])
income_res = dict([(key, re.compile(key)) for key in incomes])
