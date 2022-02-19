import os
import sys
import time
import json
import requests
from collections import OrderedDict 
from datetime import datetime, timedelta
from utils.app_logger import initLogger, getLogger


def setLogger(app_name, log_dir, conf):
    try:
        os.makedirs(log_dir)
    except OSError:
        if os.path.isdir(log_dir): 
            pass
        else: 
            print ('Cannot create output folder - %s' % log_dir)
    except Exception as err:
        print ('Cannot create output folder - %s, Exception - %s' % (log_dir, str(err)))
    return initLogger(app_name, log_dir, conf)


def safe_int(a, defaultVal=0) :
    try: return int(a)
    except: return defaultVal


def send_telegram_msg(message, conf):
    logger = getLogger()
    conf["message"] = message
    url = conf["api_url"].format(**conf)  
    try:
        resp = requests.get(url)   
        # print(resp.text)
        if resp.status_code == 200 and resp.ok == True:
            logger.info("Telegram Message Sent Succesful")
            return True
        else:
            logger.error("Telegram Message Failed, Status Code: %s, Full Response: %s" % (resp.status_code, resp.text))                                                                                                                                                                                                                                             
    except Exception as e:
        logger.exception("Exception in telegram send, Err: %s" % str(e))
    return False


def timestamp_to_tick(ts):
    return int(ts) % 86400
