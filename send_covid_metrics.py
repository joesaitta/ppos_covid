#!/usr/bin/python3
"""
Retrieve COVID percent positivity metrics from VA department of health
get today's information, then send it to IFTT
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import iftt_key

event = 'covid_message'
IFTT_KEY = iftt_key.key
IFTT_URL = f'https://maker.ifttt.com/trigger/{event}/with/key/{IFTT_KEY}'
FCPS_COVID_URL = 'https://www.fcps.edu/return-school/fcps-confirmed-covid-19-case-reporting'
VA_URL = 'https://data.virginia.gov/resource/3u5k-c2gr.json?health_district=Fairfax'

def get_covid_data(url):
    # Retrieve just the Fairfax data
    data = pd.read_json(VA_URL)

    # Clean the Not Reported line (I think if it's looking at today)
    data = data[data.lab_report_date != 'Not Reported'].copy()
    data['lab_report_date'] = pd.to_datetime(data.lab_report_date)
    
    # Start filtering
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = now - timedelta(days=14)
    last14 = data[start <= data.lab_report_date]
    
    # Percent positive
    ntests = last14.total_number_of_testing.sum()
    npos = last14.total_number_of_positive.sum()
    return npos / ntests


def send_alert(metric1):
    """
    Send the body of the message to IFTT
    IFTT ingredients are ['EventName', 'Value1', 'Value2', 'Value3', 'OccuredAt']
    """
    alert = {}
    alert['value1'] = metric1
    alert['value2'] = None
    alert['value3'] = FCPS_COVID_URL
    requests.post(IFTT_URL, json=alert)


if __name__ == "__main__":
    ppos = get_covid_data(VA_URL) * 100
    metric1 = f'{ppos:.2f}%'
    send_alert(metric1)

