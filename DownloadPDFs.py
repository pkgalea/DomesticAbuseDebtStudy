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
    print (df_d.shape)
    for _,r in df_d.iterrows():
        decree = r[column_name] 
        cause_num = r["Cause Number"]
        if decree:
 #           print("downloaded: " + decree)
            source = "../Downloads/" + decree.split("=")[1] + ".pdf"
            dest = "decrees/" + cause_num + "_" + str(i) + ".pdf"
            files_to_move.append((source, dest))
            if os.path.exists(source):
                print("Already Downloaded: " + cause_num)
                files_to_move.append((source, dest))
            elif os.path.exists(dest):
                print("Already Moved:" + cause_num)
            else:
                print("Downloading: " + cause_num)
                driver.get(decree) 
                files_to_move.append((source, dest))           
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
    