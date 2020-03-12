import pandas as pd
from selenium import webdriver
import os
import math
from SeleniumDriver import SeleniumDriver
import time

class PDFDownloader:
    """ 
        Constructor for PDFDownloader.  Logs into travis county website

        Parameters: None

        Returns:  None
    """
    def __init__(self):
        self.selenium_driver = SeleniumDriver ()
        self.selenium_driver.log_in()
        self.files_to_move = []         

    """ 
        Gets the list of decrees to download and move

        Parameters: 
        df(DataFrame): The rows from the csv file from which to download a pdf
        i (int):  The decree to download.  0, 1, 2, etc...  (only applicable if there are mutliple decrees)

        Returns:  None
    """
    def get_decrees(self, df, i):
        column_name = "Decree" + str(i)
        if (column_name) not in df.columns:
            return False
        df_d = df[~df[column_name].isna()]
        for _,r in df_d.iterrows():
            decree = r[column_name] 
            cause_num = r["Cause Number"]
            if decree:
                source = "../Downloads/" + decree.split("=")[1] + ".pdf"
                dest = "decrees/" + cause_num + "_" + str(i) + ".pdf"
                if os.path.exists(source):
                    print("Already Downloaded: " + cause_num)
                    self.files_to_move.append((source, dest))
                elif os.path.exists(dest):
                    print("Already Moved:" + cause_num)
                else:
                    print("Downloading: " + cause_num)
                    self.selenium_driver.driver.get(decree) 
                    self.files_to_move.append((source, dest))           
                    time.sleep(2)
                
        return True


    def move_decrees(self):
     """ 
        Moves the downloaded PDFs to the decree folder.

        Parameters: None

        Returns:  None
    """
        for source, dest in self.files_to_move:
            print ("moving: ", source, dest)
            if os.path.exists(source):
                print(os.rename(source, dest))
            else:
                print(source + " not found")

    def download_pdfs(self):
    """ 
        Downloads the pdfs for the decree and moves them to the decree folder

        Parameters: None

        Returns:  None
    """
        df = pd.read_csv("csv/Records.csv")
        df = df[~df.Use.isna()]
        i = 1
        while self.get_decrees(df, i):
            i+=1
        print(self.files_to_move)
        self.move_decrees()

if __name__ == "__main__": 
    pdf_downloader = PDFDownloader()
    pdf_downloader.download_pdfs()
