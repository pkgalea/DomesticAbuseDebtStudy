import requests
import time
from bs4 import BeautifulSoup
import json
import os.path
from os import path
from selenium import webdriver
from SeleniumDriver import SeleniumDriver

class CaseDownloader:
    """ 
        CaseDownloader:  Class that logs into the Travis Country Clerk Website and downloads the case information for a given year by iterating over
        case numbers starting at 1 until it doesn't find a record for 50 cases.
        Stores the files as json objects to a folder
    """

    def __init__(self):
        """ 
            Constructor for the CaseDownloader class.  Logs into Travis County website.

            Parameters: None
            Returns:  None
        """
        self.selenium_driver = SeleniumDriver()
        self.selenium_driver.log_in()

    def parse_table(self, table_class):
        """ 
            Parses a table on a web page and stores the info in a dictionary

            Parameters: 
            table_class(string):  The class of the table to be parsed

            Returns:  
            dict: The dictionary of the parsed table
        """
        events = self.selenium_driver.driver.find_element_by_class_name(table_class).get_attribute('innerHTML')
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

    def fill_in_webform_fields(self, year, record_num):
        """ 
            Enters the year, record number, and 'F' (for family) on the courthouse website.

            Parameters: 
            year(int): The year of the court case
            record_num(str): The number of the record found
            Returns:  None
        """
        driver = self.selenium_driver.driver
        time.sleep(2)
        driver.find_element_by_id("CauseYear").send_keys(str(year))
        driver.find_element_by_id("CauseNumber").send_keys(record_num)
        driver.find_element_by_id("CauseType").send_keys("F")
        driver.find_element_by_css_selector(".btn-primary").click()
        time.sleep(1)

    def dump_not_found_record(self, record_num, jfile):
        """ 
            Writes an empty file for a missing record

            Parameters: 
            record_num(str): The number of the record found
            jfile(string): The file to be written to

            Returns:  None
        """       
        print(record_num + " NOT FOUND")
        with open(jfile, 'w') as fp:
            json.dump({}, fp)

    def dump_found_record(self, record_num, jfile):
        """ 
            Writes a file for a found record 

            Parameters: 
            record_num(str): The number of the record found
            jfile(string): The file to be written to

            Returns:  None
        """
        details = self.selenium_driver.driver.find_element_by_id("detailsSummary").get_attribute('innerHTML')
        summary_dict = {"record_num":record_num}
        for dt in details.split("<dt>")[1:]:
            key = dt.split('</dt>')[0].strip()
            val = dt.split('<dd>')[1].split('</dd>')[0].strip()
            summary_dict [key]=val
        summary_dict["parties"] = self.parse_table("app-party-table")
        summary_dict["events"] = self.parse_table("app-event-table")
        with open(jfile, 'w') as fp:
            json.dump(summary_dict, fp)
        print (record_num + " written")  

    def get_records_for_year(self, year, start_record=1):
        """ 
            Gets all the records for a particular year from the Travis County Courthouse website

            Parameters: 
            year (int): The year to be scraped (either 18, 19, 20)
            start_record: The record number to start on

            Returns:  None
        """
        driver = self.selenium_driver.driver
        i = start_record
        not_found_count = 0
        while (not_found_count < 50):   #stop after 50 not founds (that's probably the last of the records)
            record_num = str(i).rjust(6, "0")
            jfile = 'json' + str(year) + '/'+record_num+'.json'
            if (path.exists(jfile)):
                print (record_num + " already exists")
                i+=1
                continue          
            self.fill_in_webform_fields(year, record_num)
            if "unable to locate" in driver.page_source:
                self.dump_not_found_record(record_num, jfile)
                not_found_count += 1
            else:
                not_found_count = 0
                self.dump_found_record(record_num, jfile)
            driver.get ("https://public.traviscountytx.gov/aaro/") 
            i += 1
        self.selenium_driver.close()


if __name__ == "__main__": 
    case_downloader = CaseDownloader()
    case_downloader.get_records_for_year(19)

