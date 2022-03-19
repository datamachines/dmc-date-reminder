#!/usr/bin/python3
import yaml
import requests
import csv
import sys
import json
from datetime import datetime, timedelta
from os.path import expanduser
import time

config_file = expanduser("~") + "/.datereminder/config_ms.yml"
#print (config_file)
mmdd = datetime.now().strftime("%m-%d")
yyyy = datetime.now().strftime("%Y")
yyyymmdd = date = datetime.now().strftime("%Y-%m-%d")
todayObj = datetime.strptime(yyyymmdd, "%Y-%m-%d")
#print(todayObj)
try:
    config = yaml.safe_load(open(config_file))
except:
    print ("Unable to read config file.")
    sys.exit(0)


def slack(chan, text):
    payload = {
        "text": text,
        "channel": chan,
        "icon_emoji": config['icon_emoji'],
        "username": config['username']
    }
    slackr = requests.post(config['webhook'], data=json.dumps(payload))
    print ("Slack response:", slackr.text)
    time.sleep(1)


def is_valid_year(year):
    if year and year.isdigit():
        if int(year) >= 1900 and int(year) <= 2100:
            return True
    return False


csv_r = requests.get(config['downloadurl'])
if csv_r.status_code != 200:
    print ("Unable fo fetch spreadsheet. Not a 200 status code.")
    sys.exit(0)
print("Loaded CSV")

ss = list(csv.reader(csv_r.text.split('\n')))
header = ss[0]
headerN = {}
for cellN in range(0, len(header)):
    headerN[header[cellN].strip().lower()] = cellN

d_channel= "#dmc-deliverables"
linen = 1
for row in ss[1:]:
    linen += 1
    record = {}
    for n in range(0, len(row)):
        for hcol in headerN.keys():
            if headerN[hcol] == n:
                if row[n].strip() != '':
                    record[hcol] = row[n]
    if all(col in record.keys()
           for col in ['submit', 'name', 'program']):
        rec_date_obj = datetime.strptime(record['submit'], "%m-%d-%Y")

        if 'days prior' in record:
            days_prior = record['days prior']
        else:
            days_prior = 10
        rec_alert_date_obj = datetime.strptime(record['submit'], "%m-%d-%Y") - timedelta(days=int(days_prior))

        if 'days post' in record:
            days_post = record['days post']
        else:
            days_post = 10
        rec_stop_date_obj  = datetime.strptime(record['submit'], "%m-%d-%Y") + timedelta(days=int(days_post))

        if 'channel' in record:
            channel = record['channel']
        else:
            channel = d_channel
        
        text = ""
        icon = ""

        if todayObj >= rec_alert_date_obj and todayObj <= rec_date_obj:
            icon = ":graph:"  
            days = (rec_date_obj - todayObj).days
            daystext = " -- in " + str(days) + " day"
            if days > 1:
                daystext += "s"
            elif days == 0:
                daystext = " -- today"
            if 'submitted on' in record:
                daystext = ""
            text = record['name'] + daystext + " (is due on " + record['submit'] + ")"

        if todayObj <= rec_stop_date_obj and todayObj > rec_date_obj:
            icon = ":rotating_light:"
            days = (todayObj - rec_date_obj).days
            daystext = " !! past due " + str(days) + " day"
            if days > 1:
                daystext += "s"
            elif days == 0: # do not think we will ever trigger that one :)
                daystext = " !! today"
            if 'submitted on' in record:
                daystext = ""
            text = record['name'] + daystext + " (was due on " + record['submit'] + ")"

        if 'submitted on' in record:
           icon = ":white_check_mark:"

        if text != "":
            text = text + " [line " + str(linen) + " in " + config['presenturl'] + "]"
            print (channel + " | " + record['program'] + " " + icon + " " + text)
            slack (channel, record['program'] + " " + icon + " " + text)
