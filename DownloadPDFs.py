import pandas as pd
from selenium import webdriver
import os
import math
from SeleniumDriver import log_in
import time

def get_decrees(driver, df, i, files_to_move):
    column_name = "Decree" + str(i)
    if (column_name) not in df.columns:
        return False
    df_d = df[~df[column_name].isna()]
    for _,r in df_d.iterrows():
        decree = r[column_name] 
        cause_num = r["Cause Number"]
        if decree:
            print("downloaded: " + decree)
            files_to_move.append(("../Downloads/" + decree.split("=")[1] + ".pdf", "decrees/" + cause_num + "_" + str(i) + ".pdf"))
 #           downloaded_files.append("../Downloads/" + decree.split("=")[1] + ".pdf")
            driver.get(decree) 
            time.sleep(2)
    return True


def move_decrees(files_to_move):
    for source, dest in files_to_move:
        print ("moving: ", source, dest)
        if os.path.exists(source):
            print(os.rename(source, dest))
        else:
            print(source + " not found")


df = pd.read_csv("csv/Records.csv")
df = df[~df.Use.isna()]
driver = log_in()
i = 1
files_to_move = []
while get_decrees(driver, df, i, files_to_move):
    i+=1
i=1
print(files_to_move)
move_decrees(files_to_move)

#while move_decrees(df, i):
#    i += 1
#driver.close()
    