#!/usr/bin/python3
import yaml
import requests
import csv
import sys
import json
from datetime import datetime, timedelta
from os.path import expanduser
import time
from collections import defaultdict

config_file = expanduser("~") + "/.datereminder/config.yml"
config_file = "/home/s/dmc/dmc-date-reminder/data/zippy/conf/config.yml"

#print (config_file)
mmdd = datetime.now().strftime("%m-%d")
yyyy = datetime.now().strftime("%Y")
yyyymmdd = date = datetime.now().strftime("%Y-%m-%d")
todayObj = datetime.strptime(yyyymmdd, "%Y-%m-%d")
fail_channel = "#test-tube"
#print(todayObj)
try:
    config = yaml.safe_load(open(config_file))
    defaults= config["default"]

except:
    print ("Unable to read config file.")
    sys.exit(0)


def slack(payload):
    print(str(payload))
    # slackr = requests.post(config['webhook'], data=json.dumps(payload))
    # print ("Slack response:", slackr.text)
    # time.sleep(1)


    # slack(payload)

def slack_fail_payload(text = ":gear: GladOS needs service "):
    payload = {
        "text": text,
        "channel": "#test-tube",
    }
    slack(payload)

def is_valid_year(year):
    if year and year.isdigit():
        if int(year) >= 1900 and int(year) <= 2100:
            return True
    return False


def get_csv():
    try:
        csv_data = requests.get(config['downloadurl'])
        if csv_data.status_code != 200:
            print("Unable fo fetch spreadsheet. Not a 200 status code.")
            sys.exit(0)
        print("Loaded CSV")
        csvreader = csv.DictReader(csv_data.text.split('\n'))
        return csvreader
    except:
        slack_fail_payload()

# def create_full_message:

def fill_payload(row):
    l_row = dict((k.lower().strip(), v) for k, v in row.items())
    type = l_row.get("type")

    template_config = defaults
    template_config.update(config.get(type.lower(), template_config))

    ## ordinal, mm-dd , text, message , until_date, event_day

    ordinal = ""
    until_date = ""
    days = 0
    template_text = template_config.get("prior_message")
    if 'year' in l_row.keys() and is_valid_year(l_row['year']):
        rec_date_obj = datetime.strptime(l_row['year'] + "-" + l_row['mm-dd'],
                                         "%Y-%m-%d")
        rec_alert_date_obj = datetime.strptime(
            l_row['year'] + "-" + l_row['mm-dd'],
            "%Y-%m-%d") - timedelta(days=int(l_row['days prior']))
    else:
        rec_date_obj = datetime.strptime(yyyy + "-" + l_row['mm-dd'],
                                         "%Y-%m-%d")
        rec_alert_date_obj = datetime.strptime(
            yyyy + "-" + l_row['mm-dd'],
            "%Y-%m-%d") - timedelta(days=int(l_row['days prior']))
    #        print(todayObj, " | ", rec_alert_date_obj, " | ", rec_date_obj)

    if todayObj >= rec_alert_date_obj and todayObj <= rec_date_obj:
        days = (rec_date_obj - todayObj).days
        until_date = " in " + str(days) + " day"
        if days > 1:
            until_date += "s"
        elif days == 0:
            until_date = " today"
            template_text = template_config.get("now_message")


    if todayObj >= rec_alert_date_obj and todayObj <= rec_date_obj:
        days = (rec_date_obj - todayObj).days
        until_date = " in " + str(days) + " day"
        if days > 1:
            until_date += "s"
        elif days == 0:
            until_date = " today"
            template_text = template_config.get("now_message")


    if "ordinal" in template_text:
        year =  todayObj.year - rec_date_obj.year
        ordinal = config["template_keys"]["ordinal"][year]

    template_data = {
        "event_day": l_row["mm-dd"],
        "text":l_row["text"],
        "message": l_row["message"],
        "until_date": until_date,
        "event_day":l_row["mm-dd"],
        "ordinal": ordinal
    }

    full_text = template_text.format(**template_data)
    payload = {
        "text": full_text,
        "channel": l_row.get("channel", fail_channel),
        "icon_emoji": template_config.get("icon_emoji"),
        "username": template_config.get("username"),
    }
    slack(payload)

    # template_instant = template["instant"]
    # template_prior = template["prior"]
    # channel = l_row.get("channel", "fail-log")
    # icon_emoji = template.get('icon_emoji', "")
    # username = template.get('username', "GladOS")






    ## ordinal, mm-dd , text, message , until_date, event_day


if __name__ == "__main__":
    dict_rows = get_csv()
    for row in dict_rows:
        fill_payload(row)
