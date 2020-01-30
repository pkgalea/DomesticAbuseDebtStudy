import json
import gender_guesser.detector as gender
import numpy as np
from os import path

d = gender.Detector()
    
def get_records():
    # READ JSON FILES INTO RECORDS
    records = []
    for y in [17, 18, 19]:
        for i in range(1, 10000):
            filename = 'json' + str(y) + '/' + str(i).rjust(6, "0") + '.json'
            if (path.exists(filename)):
                with open(filename) as json_file:
                    data = json.load(json_file)
                    if (len(data)>0):
                        if "DIVORCE" in data["Type"] and data["Case Status"]=="CLOSED":
                            records.append(data)
    return records




def write_headers(records, csv_file):

    max_parties = max([len(r['parties']) for r in records])
    max_decrees = max([len([e for e in r["events"] if e['Description'].startswith('ORD:DECREE DIVORCE')]) for r in records])

    csv_file.write('Use')
    fields = ['Cause Number', 'Filed Date', 'Case Status', 'Hetero']
    for f in fields:
        csv_file.write("," + f)
      

    for i in range (2):
        csv_file.write(',Gender'+str(i+1))
        csv_file.write(',Party - FirstNames'+str(i+1))
        csv_file.write(',Party - Surname'+str(i+1))
        csv_file.write(',Type'+str(i+1))
        csv_file.write(',Attorney'+str(i+1))
        
    for i in range(max_decrees):
        csv_file.write(',Decree Date' + str(i+1))
        csv_file.write(',Decree' + str(i+1))
        
    fields = ['Style', 'Court', 'Type', 'Hearing Date']
    for f in fields:
        csv_file.write("," + f)

    for i in range(2, max_parties):
        print(i)
        csv_file.write(',Gender'+str(i+1))
        csv_file.write(',Party - FirstNames'+str(i+1))
        csv_file.write(',Party - Surname'+str(i+1))
        csv_file.write(',Type'+str(i+1))
        csv_file.write(',Attorney'+str(i+1))


    csv_file.write("\n")
    return max_parties, max_decrees
    

    
def split_and_get_gender(p):

    surname, firstnames, gender = "", "", ""
    full_name = p['Party - Person']
    if ',' in full_name:
        comma_split = full_name.split(',')
        surname = comma_split[0]
        firstnames = comma_split[1]

        fnames = firstnames.strip().split(" ")
        first_name = fnames[0].lower().capitalize()
        gender = d.get_gender(first_name)
        if (gender not in ['male', 'female', 'mostly_male', 'mostly_female'] and len(fnames) > 1):
            for f in fnames[1:]:
                if (f):
                    middle_name = f.lower().capitalize()
                    gender = d.get_gender(middle_name)
        surname = surname.strip()
        firstnames = firstnames.strip()
        gender = gender
    return surname, firstnames, gender    
    
def deal_with_parties(r):
    for p in r['parties']:
        p["surname"], p["firstnames"], p["gender"] = split_and_get_gender(p)    

    business_respondent = [x for x in r['parties'] if x['Type'] == "RESPONDENT" and x['Party - Full/Business'] ]
    business_petitioner = [x for x in r['parties'] if x['Type'] == "PETITIONER" and x['Party - Full/Business'] ]

    respondent = [x for x in r['parties'] if x['Type'] == "RESPONDENT" and not x['Party - Full/Business'] ]
    petitioner = [x for x in r['parties'] if x['Type'] == "PETITIONER" and not x['Party - Full/Business'] ]

    if (len(respondent) > 1):
        res_name = respondent[0]['Party - Person']
        for res in respondent[1:]:
            if res['Party - Person'] == res_name:
                respondent.remove(res)

    if (len(petitioner) > 1):
        pet_name = petitioner[0]['Party - Person']
        for pet in petitioner[1:]:
            if pet['Party - Person'] == pet_name:
                petitioner.remove(pet)
      
    
    if not (len(respondent)==1 and len(petitioner)==1):
        print(r['Cause Number'] + " Respondents: " + str(len(respondent)) + " Petitioners: " + str(len(petitioner)))
        print("RESPONDENTS:")
        for res in respondent:
            print("   ", res)
        print("PETITIONERS:")
        for pet in petitioner:
            print("   ", pet)
        print("**************************************") 
        print( "")
        print("")
 
    r['other_parties'] = [x for x in r['parties'] if x['Type'] not in ["RESPONDENT", "PARITIONER"]]

    if len(respondent) == 0 or len(petitioner)==0:
#        print("NO PETITIONER OR RESPONDENT")
        r["resp_and_part"] = []
        r["other_parties"]
        r["Hetero"] = "Unknown"
    else:
        resp_and_part = [respondent[0], petitioner[0]]
#        print(resp_and_part)
        r['resp_and_part'] = sorted(resp_and_part, key = lambda i: i['gender'] not in ['female', 'mostly_female'])

        if len(r['resp_and_part'])>=2:
            g1 = r['resp_and_part'][0]['gender']
            g2 = r['resp_and_part'][1]['gender']
            sorted_gs = sorted([g1, g2])
            if sorted_gs in (['female', 'male'], ['male', 'mostly_female'], ['female', 'mostly_male'], ['mostly_female', 'mostly_male']):
                r["Hetero"]="Hetero"
            elif sorted_gs in (['female', 'female'], ['male', 'mostly_male'], ['female', 'mostly_female'], ['mostly_male', 'mostly_male']):
                r["Hetero"]="Same Sex"
            else:
                r["Hetero"]="Unknown"

        else:
            print("UH OH")
            r["Hetero"]="Unknown"
    



with open ('csv/Records.csv', 'w') as csv_file:
    records = get_records()
    max_parties, max_decrees = write_headers(records, csv_file)
    for r in records:
 
        deal_with_parties(r)

        
        fields = ['Cause Number', 'Filed Date', 'Case Status', 'Hetero']
        for f in fields:
            csv_file.write("," + r[f])
        

        for p in r['resp_and_part']:
            for v in [list(p.values())[x] for x in [6, 5, 4, 1, 0]]:
                csv_file.write(','+v) 
        
        
        decrees = [e for e in r["events"] if 'ORD:DECREE DIVORCE' in e['Description']]
        for e in decrees:
            url = e['&nbsp;']
            url = url.split('"')[1]
            url = url.split('"')[0]
            csv_file.write("," + e["Date"] + ',=HYPERLINK("' + 'https://public.traviscountytx.gov' + url + '")')

        for i in range(max_decrees-len(decrees)):    
            csv_file.write(",,")
         
        fields = ['Style', 'Court', 'Type', 'Hearing Date']
        for f in fields:
            csv_file.write("," + r[f])
 
        for p in r['other_parties']:
            for v in [list(p.values())[x] for x in [6, 5, 4, 1, 0]]:
                csv_file.write(','+v) 

        csv_file.write("\n")