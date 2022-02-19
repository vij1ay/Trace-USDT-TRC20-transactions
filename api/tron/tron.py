import json
import requests
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from urllib import parse
from utils.utility import *
logger = getLogger()


def getInst(config):
    return Tron(config)

class Tron:
    def __init__(self, config):
        self.config = config
        self.scheduler = BackgroundScheduler()

    def initData(self):
        self.last_check_fp = "lastchk_%s.dat" % self.config["APP"]["trace_address"]
        print ("self.last_check_fp >> ", self.last_check_fp)
        self.last_check_time = self.getLastChkTime(self.last_check_fp)
        print ("self.last_check_fp", self.last_check_time)


    def initThreads(self):
        logger.info ("In tron initThreads")
        # threading.Thread(target=self.fetchData).start()
        threading.Thread(target=self.addSchedules).start()


    def getLastChkTime(self, file_pointer):
        try:
            with open(file_pointer,'r') as f:
                return safe_int(f.read().strip()) 
        except:
            with open(file_pointer,'w+') as f:
                f.write('0')
            return 0


    def updateLastChkTime(self, file_pointer, chktime):
        self.last_check_time = chktime
        with open(file_pointer,'w+') as f:
            f.write(str(chktime)) 


    def addSchedules(self):
        logger.info ("In Tron addSchedules, chk time - %s" % self.config["APP"].get("trace_summary_at", "00:00:01"))
        hr, min, sec = self.config["APP"].get("trace_summary_at", "23:59:59").split(":")
        self.scheduler.add_job(self.getDaySummary, 'cron', hour=hr, minute=min, second=sec)
        self.scheduler.add_job(self.getSuccessTransactions, 'interval', seconds=safe_int(self.config["APP"].get("trace_interval", "300")))
        self.scheduler.start()


    def getSuccessTransactions(self):
        chk_time = (int(time.time()) * 1000)
        api_url = self.config["TRON"]["get_success_transactions_url"].format(min_timestamp=self.last_check_time, max_timestamp=chk_time - 1)
        # print ("full url -- > ", api_url # 1622627335449
        logger.info("Getting Success Transactions, API URL -> %s" % api_url)
        transaction_msg = "Transaction Id: %s\nAmount: %s\nAsset: %s\nOwner Address: %s\nTo Address: %s\nType: %s\nContract Time: %s\nExpiry Time: %s\nFee: %s"
        try:
            resp = requests.get(api_url)
            response = resp.json()
            if response.get("success"):
                self.updateLastChkTime(self.last_check_fp, chk_time)
                for data in response.get("data", []):
                    # print (data)
                    txId = data.get("txID")
                    amount = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("amount")
                    asset = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("asset_name")
                    owner = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address")
                    to = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address")
                    ctype = data.get("raw_data", {}).get("contract", [{}])[0].get("type")
                    ctime = time.ctime(safe_int(data.get("raw_data", {}).get("timestamp")) / 1000)
                    etime = time.ctime(safe_int(data.get("raw_data", {}).get("expiration")) / 1000)
                    fee = data.get("ret", [{}])[0].get("fee")
                    contract_detail = transaction_msg % (txId, amount, asset, owner, to, ctype, ctime, etime, fee)
                    send_telegram_msg(contract_detail, self.config["TELEGRAM"])
        except:
            logger.exception("Error in getSuccessTransactions")
            pass


    def getDaySummary(self):
        print ("in getDaySummary")
        current_time = int(time.time())
        st = (current_time - (current_time%86400) - 86400) * 1000 # last day start time
        et = ((current_time - (current_time%86400)) * 1000) - 1 # last day end time
        print (time.ctime(st/1000),time.ctime(et/1000))
        # st = 1622637494124 # for testing
        # et = 1639684196187 # for testing
        api_url = self.config["TRON"]["get_transactions_url"].format(min_timestamp=st, max_timestamp=et)
        logger.info("Getting All Transactions for Last Day, API URL -> %s" % api_url)
        try:
            resp = requests.get(api_url)
            response = resp.json()
            # print (response)
            if response.get("success"):
                transaction_msg = "Transaction Id: %s\nAmount: %s\nAsset: %s\nOwner Address: %s\nTo Address: %s\nType: %s\nContract Time: %s\nExpiry Time: %s\nFee: %s\n"
                contract_summary = "Transaction Summary from %s to %s\n" % (time.ctime(st/1000), time.ctime(et/1000))
                total_transactions = 0
                total_in = 0
                total_out = 0
                total_net = 0
                for data in response.get("data", []):
                    # print (data)
                    total_transactions += 1
                    contract_summary += "\n----- %s -----\n" % total_transactions
                    txId = data.get("txID")
                    amount = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("amount")
                    asset = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("asset_name")
                    owner = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address")
                    to = data.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address")
                    ctype = data.get("raw_data", {}).get("contract", [{}])[0].get("type")
                    ctime = time.ctime(safe_int(data.get("raw_data", {}).get("timestamp")) / 1000)
                    etime = time.ctime(safe_int(data.get("raw_data", {}).get("expiration")) / 1000)
                    fee = data.get("ret", [{}])[0].get("fee")
                    contract_summary += transaction_msg % (txId, amount, asset, owner, to, ctype, ctime, etime, fee)
                    total_net += safe_int(amount)
                contract_summary += "\nTotal Transactions Count - %s" % total_transactions
                contract_summary += "\nNet Total - %s" % total_net
                send_telegram_msg(contract_summary, self.config["TELEGRAM"])
        except:
            logger.exception("Error in getSuccessTransactions")
            pass


"""
# import requests
# url = "https://api.shasta.trongrid.io/v1/accounts/TSaJqQ1AZ2bEYyqBwBmJqCBSPv8KPRTAdv/transactions?only_confirmed=true&limit=200"
# headers = {"Accept": "application/json"}
# response = requests.request("GET", url, headers=headers)
# print(response.text)
SyntaxError: expected ':'
>>> for x in xx["data"]:
...  print (x, "\n\n")
...
{'ret': [{'contractRet': 'SUCCESS',
"""

"""
sample data
{
    "ret": [
        {
            "contractRet": "SUCCESS",
            "fee": 100000
        }
    ],
    "signature": [
        "37dab30f6e35cf95e4f383e4fd10899d620ad3d2d205789cedf3c15eea54304f2c237c83433dd6e932d669492e260d99f3d6ef8ab52943faba4dec66db520b0301"
    ],
    "txID": "dfd0b11c009766b8d301bc9909abd2a65663b4106d7bf2cfd3f9a4fda4a3252d",
    "net_usage": 0,
    "raw_data_hex": "0a0270f42208f5939ff676b4982740d0c384e19c2f5a76080212720a32747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e5472616e736665724173736574436f6e7472616374123c0a07313030303737381215413d23ac580bffd1ffdf89b00e86ad7eba343188791a1541b62570d190572fca2d6f0bd9debdca13f3bbd6412080dac4097099fa80e19c2f",
    "net_fee": 100000,
    "energy_usage": 0,
    "blockNumber": 15429895,
    "block_timestamp": 1622627337000,
    "energy_fee": 0,
    "energy_usage_total": 0,
    "raw_data": {
        "contract": [
            {
                "parameter": {
                    "value": {
                        "amount": 20000000,
                        "asset_name": "1000778",
                        "owner_address": "413d23ac580bffd1ffdf89b00e86ad7eba34318879",
                        "to_address": "41b62570d190572fca2d6f0bd9debdca13f3bbd641"
                    },
                    "type_url": "type.googleapis.com/protocol.TransferAssetContract"
                },
                "type": "TransferAssetContract"
            }
        ],
        "ref_block_bytes": "70f4",
        "ref_block_hash": "f5939ff676b49827",
        "expiration": 1622627394000,
        "timestamp": 1622627335449
    },
    "internal_transactions": []
}
"""