import json
import gender_guesser.detector as gender
import numpy as np
from os import path
from datetime import datetime

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
                        if "DIVORCE" in data["Type"]:  #and data["Case Status"]=="CLOSED":
                            decrees = get_decrees(data["events"])
                            if (decrees):
                                first_decree_date = decrees[0]["Date"]
                                date_parts = first_decree_date.split("/")
                                if date_parts[0]=="1" and date_parts[2]=="2020":
                                    records.append(data)
    return records

def convert_date(d):
    if d:
        return str(datetime.strptime(d, '%m/%d/%Y').date())
    return ""

def convert_dates(records):
    for r in records:
        r['Filed Date'] = convert_date(r['Filed Date'])
 

def write_headers(records, csv_file):

    max_parties = max([len(r['parties']) for r in records])
    max_decrees = max([len([e for e in r["events"] if e['Description'].startswith('ORD:DECREE DIVORCE')]) for r in records])

    csv_file.write('Use')
    fields = ['Cause Number', 'Type', 'Filed Date', 'Case Status', '1P1R', 'Hetero']
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
        
    fields = ['Style', 'Court', 'Hearing Date']
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

def assign_hetero (g1, g2):
    sorted_gs = sorted([g1, g2])
    if sorted_gs in (['female', 'male'], ['male', 'mostly_female'], ['female', 'mostly_male'], ['mostly_female', 'mostly_male']):
        return "Hetero"
    elif sorted_gs in (['male', 'male'], ['female', 'female'], ['male', 'mostly_male'], ['female', 'mostly_female'], ['mostly_male', 'mostly_male'], ['mostly_female', 'mostly_female']):
        return "Same Sex"
    else:
        return "Unknown"


def deal_with_parties(r):
    for p in r['parties']:
        p["surname"], p["firstnames"], p["gender"] = split_and_get_gender(p)    

    other_respondents = [x for x in r['parties'] if x['Type'] == "RESPONDENT" and x['Party - Full/Business'] ]
    other_petitioners = [x for x in r['parties'] if x['Type'] == "PETITIONER" and x['Party - Full/Business'] ]

    respondent = [x for x in r['parties'] if x['Type'] == "RESPONDENT" and not x['Party - Full/Business'] ]
    petitioner = [x for x in r['parties'] if x['Type'] == "PETITIONER" and not x['Party - Full/Business'] ]

    r['1P1R'] = "YES"

    #two responsdents, same name
    if (len(respondent) > 1):
        res_name = respondent[0]['Party - Person']
        for res in respondent[1:]:
            if res['Party - Person'] == res_name:
                other_respondents.append(res)
                respondent.remove(res)

    # two petitioners, same name
    if (len(petitioner) > 1):
        pet_name = petitioner[0]['Party - Person']
        for pet in petitioner[1:]:
            if pet['Party - Person'] == pet_name:
                other_petitioners.append(pet)
                petitioner.remove(pet)
    
    # 2 partitioners = mutual filing
    if (len(petitioner)==2 and len(respondent)==0):
        respondent.append(petitioner.pop())
    
    # Probably a mislabled divorce
    if len(respondent)==0 or len(petitioner)==0:
        print ("WEIRD" + r['Cause Number'])
        return False
 
    # Something weird.  Mark it.
    if  (len(respondent)>1 or len(petitioner)>1):
        r['1P1R'] = "NO"       
        other_respondents += respondent[:-1]
        other_petitioners += petitioner[:-1]
        petitioner = [petitioner[-1]]
        respondent = [respondent[-1]]


    r['other_parties'] = other_petitioners + other_respondents + [x for x in r['parties'] if x['Type'] not in ["RESPONDENT", "PETITIONER"]] 

    resp_and_part = [respondent[0], petitioner[0]]
    r['resp_and_part'] = sorted(resp_and_part, key = lambda i: i['gender'] not in ['female', 'mostly_female'])

    r['Hetero'] = assign_hetero(r['resp_and_part'][0]['gender'], r['resp_and_part'][1]['gender'])

    return True

def write_parties(parties):
    for p in parties:
        for v in [list(p.values())[x] for x in [6, 5, 4, 1, 0]]:
            csv_file.write(','+v) 

def get_decrees(events):
    decrees = [e for e in events if 'ORD:DECREE DIVORCE' in e['Description']]
    decrees = sorted(decrees, key=lambda x: datetime.strptime(x["Date"], '%m/%d/%Y').date())
    return decrees

def write_decrees(decrees):
    for e in decrees:
        url = e['&nbsp;']
        url = url.split('"')[1]
        url = url.split('"')[0]
        csv_file.write("," + convert_date(e["Date"]) + ',=HYPERLINK("' + 'https://public.traviscountytx.gov' + url + '")')
    for _ in range(max_decrees-len(decrees)):    
        csv_file.write(",,")

def write_fields(fields):
  for f in fields:
            csv_file.write("," + r[f])
        
with open ('csv/Records.csv', 'w') as csv_file:
    records = get_records()
    convert_dates(records)
    max_parties, max_decrees = write_headers(records, csv_file)
    for r in records:
 
        if not (deal_with_parties(r)):
            continue

        fields = ['Cause Number', 'Type', 'Filed Date', 'Case Status', '1P1R', 'Hetero']
        write_fields(fields)
      
        write_parties(r['resp_and_part'])
        
        write_decrees(get_decrees(r['events']))
         
        fields = ['Style', 'Court', 'Hearing Date']
        write_fields(fields)
 
        write_parties(r['other_parties'])

        csv_file.write("\n")