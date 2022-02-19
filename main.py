#!/usr/bin/app python
# -*- coding: utf-8 -*-

"""
{Description}
{License_info}
"""
# Built-in/Generic Imports
import os
import re
import sys
import json
import signal
import argparse
import importlib
import configparser
from utils.utility import *

BASE_DIR = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1])
inst = None
logger = None

def shutdown(inst, from_signal = 0):
    logger.info("***** Shutting down - %s *****" % from_signal)
    if hasattr(inst, 'stopThread'):
        if not inst.stopThread:
            setattr(inst, 'stopThread', 1)
            wait_secs = 5
            logger.info("Waiting %s seconds for threads to stop" % wait_secs)
            time.sleep(wait_secs)
            logger.info("Safe Exit")

def shutdownSignal(*args):
    global inst
    shutdown(inst, 1)

def main(APP_PATH, config):
    global inst, logger
    app_name = config["APP"]["app_name"]
    log_folder = re.sub('[\+\&\%\^\'\"\!\~\,\;\=\|\{\}\@\<\>\ \-\$]', '_', app_name)
    LOG_DIR = BASE_DIR + os.sep + "logs" + os.sep +  log_folder.lower() + os.sep
    logger = setLogger(app_name, LOG_DIR, config["LOGGER"])
    try:
        sys.path.append(APP_PATH)
        system = APP_PATH.split(os.sep)[-1]
        module = importlib.import_module(system)
        logger.info("Module Loaded >> %s" % module)
        logger.info("Log Directory >> %s" % LOG_DIR)
        inst = module.getInst(config)
        if hasattr(inst, 'initData'):
            inst.initData()
        threads_started = 0
        if hasattr(inst, 'initThreads'):
            setattr(inst, 'stopThread', 0)
            inst.initThreads()
            threads_started = 1
        run_forever = config["APP"].get("run_forever", 0)
        if threads_started or run_forever:
            while (not inst.stopThread) or run_forever:
                time.sleep(5)
        logger.info("**** Exiting Script ****")
    except KeyboardInterrupt :
        logger.info("**** Stopping Process ****")
    except:
        logger.exception("Stopping Process")
    shutdown(inst)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-app', help='App to execute', required=True)
    parser.add_argument('-config_file', help='Configuration File - Absolute or Full Path', required=True)
    args = parser.parse_args()

    app = args.app
    config_file = args.config_file
    try:
        if not config_file.endswith(".ini"):
            raise Exception("Invalid Config File - Configuration File must be .ini format")
        APP_PATH = BASE_DIR + os.sep + "api" + os.sep + app
        print("\nSYSTEM PATH : %s" % APP_PATH)
        if not os.path.exists(APP_PATH):
            raise Exception("Requested System not available.")
        if config_file.find(os.sep) == -1 and config_file.find('\\') == -1: # search conf in conf folder
            CONFIG_PATH = BASE_DIR + os.sep + "conf" + os.sep + config_file
        else:
            CONFIG_PATH = config_file
        print("CONFIG_PATH : %s\n" % CONFIG_PATH)
        if not os.path.isfile(CONFIG_PATH):
            raise Exception("Configuration File not found.")
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        if not config._sections:
            raise Exception("Configuration is empty.")
        signal.signal(signal.SIGINT, shutdownSignal)
        main(APP_PATH, config._sections)
    except Exception as err:
        logger.exception("Error : ")
        for e in err.args:
            print(e)
    sys.exit()
