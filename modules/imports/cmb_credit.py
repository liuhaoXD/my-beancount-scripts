from datetime import date

import dateparser
import eml_parser
from beancount.core import data
from beancount.core.data import Amount, Balance, Decimal, Posting, Transaction
from bs4 import BeautifulSoup

from . import (get_account_by_guess)
from .deduplicate import Deduplicate

AccountCmb = 'Liabilities:CreditCard:Young'
trade_area_list = {
    'CN': 'CNY',
    'US': 'USD',
    'JP': 'JPY',
    'HK': 'HKD'
}


class CMBCredit():

    def __init__(self, filename, byte_content, entries, option_map):
        if not filename.endswith('eml'):
            raise RuntimeError('Not CMB!')
        parsed_eml = eml_parser.eml_parser.decode_email_b(
            byte_content, include_raw_body=True)
        if '招商银行信用卡' not in parsed_eml['header']['subject']:
            raise RuntimeError('Not CMB!')
        content = parsed_eml['body'][0]['content']
        self.soup = BeautifulSoup(content, 'html.parser')
        self.content = content
        self.deduplicate = Deduplicate(entries, option_map)
        self.date = date.today()

    def change_currency(self, currency):
        if currency == '':
            return 'CNY'
        if currency not in trade_area_list:
            print('Unknown trade area: ' + currency +
                  ', please append it to ' + __file__)
            return currency
        return trade_area_list[currency]

    def get_date(self, detail_date):
        month = detail_date[0:2]
        day = detail_date[2:4]
        year = self.date.year
        ret = date(year, int(month), int(day))
        if month == '12' and ret > self.date:
            ret = ret.replace(ret.year - 1)
        return ret

    def parse(self):
        d = self.soup
        transactions = []
        # balance = d.select('#fixBand16')[0].text.replace('RMB', '').strip()
        date_range = d.select('#fixBand6 div font')
        if len(date_range) > 0:
            date_range = date_range[0].text.strip()
        else:
            date_range = d.select('#fixBand38 div font')[0].text.strip()
        transaction_date = dateparser.parse(date_range.split('-')[1].split('(')[0])
        transaction_date = date(transaction_date.year, transaction_date.month, transaction_date.day)
        self.date = transaction_date
        balance = (d.select('#fixBand18 div font')[0].text.replace('￥', '').replace('¥', '')
                   .replace(',', '').replace('--', '-').strip())
        if balance.startswith('-'):
            balance = balance[1:]
        else:
            balance = '-' + balance
        balance_entry = Balance(
            account=AccountCmb,
            amount=Amount(Decimal(balance), 'CNY'),
            meta={},
            tolerance='',
            diff_amount=Amount(Decimal('0'), 'CNY'),
            date=self.date
        )

        bands = d.select('#fixBand29 #loopBand2>table>tr')
        if len(bands) == 0:
            bands = d.select('#fixBand15 > table > tbody > tr > td > table > tbody > tr')
            if len(bands) == 0:
                print('bands is empty')
                return []

        for band in bands:
            tds = band.select('td #fixBand15 table table td')
            if len(tds) == 0:
                continue
            trade_date1 = tds[1].text.strip()
            trade_date2 = tds[2].text.strip()

            if trade_date1 == '':
                trade_date = trade_date2
            else:
                # 记账日月份大于交易日月份时，意味着该交易可能是分期等跨月交易
                time1 = self.get_date(trade_date1)
                time2 = self.get_date(trade_date2)
                if (time2.year != time1.year or time2.month != time1.month
                    or time2.day - time1.day < 0 or time2.day - time1.day > 1):
                    trade_date = trade_date2
                else:
                    trade_date = trade_date1
            time = self.get_date(trade_date)
            full_descriptions = tds[3].text.strip().split('-')
            payee = full_descriptions[0].replace(' ', ' ')
            description = '-'.join(full_descriptions[1:]).replace(' ', ' ')
            trade_currency = self.change_currency(tds[6].text.strip())
            trade_price = tds[7].text.replace('\xa0', '').strip()
            real_currency = 'CNY'
            real_price = tds[4].text.replace('￥', '').replace('¥', '').replace('\xa0', '').strip()
            print("Importing {} at {}".format(description, time))
            account = get_account_by_guess(description, '', time)
            flag = "!"
            amount = float(real_price.replace(',', ''))

            meta = {}
            meta = data.new_metadata('beancount/core/testing.beancount', 12345, meta)
            tags = []
            if payee == '支付宝':
                tags = ['alipay']
                payee = description
                description = ''
            elif payee == '财付通':
                tags = ['wechat']
                payee = description
                description = ''
            elif payee == '美团':
                tags = ['meituan']
                payee = description
                description = ''

            entry = Transaction(meta, time, flag, payee, description, tags, data.EMPTY_SET, [])

            if real_currency == trade_currency:
                data.create_simple_posting(entry, account, trade_price, trade_currency)
            else:
                trade_amount = Amount(Decimal(trade_price), trade_currency)
                real_amount = Amount(
                    Decimal(abs(round(float(real_price), 2))) / Decimal(abs(round(float(trade_price), 2))),
                    real_currency)
                posting = Posting(account, trade_amount, None, real_amount, None, None)
                entry.postings.append(posting)

            data.create_simple_posting(entry, AccountCmb, None, None)
            if not self.deduplicate.find_duplicate(entry, -amount, None, AccountCmb):
                transactions.append(entry)

        self.deduplicate.apply_beans()

        transactions.append(balance_entry)
        return transactions
