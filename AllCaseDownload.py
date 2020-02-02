import requests
import time
from bs4 import BeautifulSoup
import json
import os.path
from os import path
from selenium import webdriver
from SeleniumDriver import log_in


def parse_table(table_class):
    events = driver.find_element_by_class_name(table_class).get_attribute('innerHTML')
    rows = events.split('<TR>')
    for r in rows:
        headers = r.split('<th>')
        header_list = [h.split('</th>')[0] for h in headers[1:]]
        cells = r.split('<td')
        i = 0
        h = 0
        row_dicts = []
        row_dicts.append({})
        for c in cells[1:]:
            row_dicts[i][header_list[h]] = c.split('>')[1].split('</td')[0].strip()
            h += 1
            if (h == len(header_list)):
                h = 0
                i += 1
                row_dicts.append({})
        row_dicts.pop()
        return row_dicts



def get_records_for_year(driver, year, start_record=1):
    i = start_record
    not_found_count = 0
    while (not_found_count < 50):

        record_num = str(i).rjust(6, "0")
        jfile = 'json' + str(year) + '/'+record_num+'.json'
        if (path.exists(jfile)):
            print (record_num + " already exists")
            i+=1
            continue
        time.sleep(2)
        driver.find_element_by_id("CauseYear").send_keys(str(year))
        driver.find_element_by_id("CauseNumber").send_keys(record_num)
        driver.find_element_by_id("CauseType").send_keys("F")
        driver.find_element_by_css_selector(".btn-primary").click()
        time.sleep(1)
        if "unable to locate" in driver.page_source:
            print(record_num + " NOT FOUND")
            not_found_count += 1
            with open(jfile, 'w') as fp:
                json.dump({}, fp)

        else:
            not_found_count == 0
            details = driver.find_element_by_id("detailsSummary").get_attribute('innerHTML')
            summary_dict = {"record_num":record_num}
            for dt in details.split("<dt>")[1:]:
                key = dt.split('</dt>')[0].strip()
                val = dt.split('<dd>')[1].split('</dd>')[0].strip()
                summary_dict [key]=val
            summary_dict["parties"] = parse_table("app-party-table")
            summary_dict["events"] = parse_table("app-event-table")
            with open(jfile, 'w') as fp:
                json.dump(summary_dict, fp)
            print (record_num + " written")    

        driver.get ("https://public.traviscountytx.gov/aaro/") 
        i += 1
    driver.close() 

driver=log_in()
get_records_for_year(driver, 17, 6000)
