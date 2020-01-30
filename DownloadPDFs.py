import pandas as pd
from selenium import webdriver
import os
import math
from SeleniumDriver import log_in


def get_decrees(driver, df, i):
    column_name = "Decree" + str(i)
    if (column_name) not in df.columns:
        return False
    df_d = df[~df[column_name].isna()]
    for idx,r in df_d.iterrows():
        decree = r[column_name] 
        cause_num = r["Cause Number"]
        if decree:
            print("downloaded: " + decree)
            downloaded_file = "../Downloads/" + decree.split("=")[1] + ".pdf"
            driver.get(decree) 
    return True


def move_decrees(df, i):
    column_name = "Decree" + str(i)
    if (column_name) not in df.columns:
        return False
    df_d = df[~df[column_name].isna()]
    for idx,r in df_d.iterrows():
        decree = r[column_name] 
        cause_num = r["Cause Number"]
        if decree:
            print("moved: " + decree)
            downloaded_file = "../Downloads/" + decree.split("=")[1] + ".pdf"
            if os.path.exists(downloaded_file):
                os.rename(downloaded_file, "decrees/" + cause_num + "_" + str(i) + ".pdf")
            else:
                print(downloaded_file + " not found")
    return True


df = pd.read_csv("csv/Records.csv")
df = df[~df.Use.isna()]
driver = log_in()
i = 1
while get_decrees(driver, df, i):
    i+=1
i=1
while move_decrees(df, i):
    i += 1
driver.close()
    