# This is the python script to be run on the client's end and to be
# used in the kivy-based gui set up for the aforementioned client
import hashlib
from datetime import date


import encryption as enc
import Block
import yaml
import schedule
import time
import sys
import Pyro4
import Pyro4.util

sys.excepthook = Pyro4.util.excepthook

chain = Pyro4.Proxy("PYRO:obj_b8ceaf41de2c4c03ad61f6b9f4a1f9f3@10.42.0.106:43187")
print(chain)

first_stream = open("config.yaml", 'r')
first_temp = yaml.load(first_stream, Loader=yaml.SafeLoader)


def printEntityIDQuestion():
    print("Just a test")


def readEntityID():
    return "Test"


if (first_temp['Initial Setup'] == 'Yes'):
    with open('config.yaml') as f:
        doc = yaml.load(f)
    doc['Initial Setup'] = 'No'
    with open('file_to_edit.yaml', 'w') as f:
        yaml.dump(doc, f)
    printEntityIDQuestion()
    global EntityId
    EntityId = readEntityID()


def read():
    stream = open("config.yaml", 'r')
    global prior_config
    temp = yaml.load(stream, Loader=yaml.SafeLoader)
    if (prior_config != temp):
        global config
        config = temp
        prior_config = temp
        print(config)


def newRequest(doctype, orig, vendor, requestee):

        chain.add_block(doctype, None, date.today(), orig, vendor, requestee)


def completeRequest():
    print("Nothing")


def exit():
    global exit_status
    exit_status = 1


prior_config = {'Initial'}
config = {'First'}
numRequests = 0
exit_status = 0
EntityId = 'Initial'

schedule.every(2).seconds.do(read)
newRequest("Soc2","JPMorgan","Bloomberg","Goldman Sachs")

while exit_status == 0:
    schedule.run_pending()
    time.sleep(1)
