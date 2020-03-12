import json
import gender_guesser.detector as gender
import numpy as np
from os import path
from datetime import datetime


class CSVWriter:

    def __init__(self):
        '''
            Constructor for the CSVWrite class

            Parameters: None
            Returns None
        '''
        self.d = gender.Detector()
        self.csv_file=None
        self.records = None
        self.pre_party_fields = ['Cause Number', 'Type', 'Filed Date', 'Case Status', '1P1R', 'Hetero']
        self.post_party_fields = ['Style', 'Court', 'Hearing Date']
        
    def get_records(self):
        '''
            converts json files into a list of dictionaries

            Parameters: None

            Returns:
            str: The stripped date.  "" if d==None
        '''
        self.records = []
        for y in [19]:
            for i in range(1, 10000):
                filename = 'json' + str(y) + '/' + str(i).rjust(6, "0") + '.json'
                if (path.exists(filename)):
                    with open(filename) as json_file:
                        data = json.load(json_file)
                        if (len(data)>0) and "DIVORCE" in data["Type"]:  #and data["Case Status"]=="CLOSED":
                                decrees = self.get_decrees(data["events"])
                                if (decrees):
                                    first_decree_date = decrees[0]["Date"]
                                    date_parts = first_decree_date.split("/")
                                    if date_parts[0]=="2" and date_parts[2]=="2020":
                                        self.records.append(data)

    def convert_date(self, d):
        '''
            Converts datetime to string in m/d/y format

            Parameters:
            d(date): The date time to be converted

            Returns:
            str: The stripped date.  "" if d==None
        '''
        if d:
            return str(datetime.strptime(d, '%m/%d/%Y').date())
        return ""

    def convert_dates(self):
        '''
            Converts all filed dates to string in m/d/y format

            Parameters: None

            Returns: None
        '''
        for r in self.records:
            r['Filed Date'] = self.convert_date(r['Filed Date'])
    

    def write_headers(self):
        '''
            Writes the header (first row) of the excel spreadsheet

            Parameters: None
            Returns None
        ''' 
        max_parties = max([len(r['parties']) for r in self.records])
        max_decrees = max([len([e for e in r["events"] if e['Description'].startswith('ORD:DECREE DIVORCE')]) for r in self.records])

        self.csv_file.write('Use')
        for f in self.pre_party_fields:
            self.csv_file.write("," + f)
        
        for i in range (2):
            self.csv_file.write(',Gender'+str(i+1))
            self.csv_file.write(',Party - FirstNames'+str(i+1))
            self.csv_file.write(',Party - Surname'+str(i+1))
            self.csv_file.write(',Type'+str(i+1))
            self.csv_file.write(',Attorney'+str(i+1))
            
        for i in range(max_decrees):
            self.csv_file.write(',Decree Date' + str(i+1))
            self.csv_file.write(',Decree' + str(i+1))
            
        for f in self.post_party_fields:
            self.csv_file.write("," + f)

        for i in range(2, max_parties):
            print(i)
            self.csv_file.write(',Gender'+str(i+1))
            self.csv_file.write(',Party - FirstNames'+str(i+1))
            self.csv_file.write(',Party - Surname'+str(i+1))
            self.csv_file.write(',Type'+str(i+1))
            self.csv_file.write(',Attorney'+str(i+1))

        self.csv_file.write("\n")
        return max_parties, max_decrees
        

    def split_and_get_gender(self, p):
        '''
            Takes a party and returns the first and last names and assumed gender
            Parameters: 
                p(list(str)): The party scraped from the webpage
            Returns:
                str, str, str: first name, last name, gender
        ''' 
        surname, firstnames, gender = "", "", ""
        full_name = p['Party - Person']
        if ',' in full_name:
            comma_split = full_name.split(',')
            surname = comma_split[0]
            firstnames = comma_split[1]
            fnames = firstnames.strip().split(" ")
            first_name = fnames[0].lower().capitalize()
            gender = self.d.get_gender(first_name)
            if (gender not in ['male', 'female', 'mostly_male', 'mostly_female'] and len(fnames) > 1):
                for f in fnames[1:]:
                    if (f):
                        middle_name = f.lower().capitalize()
                        gender = self.d.get_gender(middle_name)
            surname = surname.strip()
            firstnames = firstnames.strip()
            gender = gender
        return surname, firstnames, gender    

    def assign_hetero (self, g1, g2):
        '''
            Determines if the relationship is same sex, hetero or unkown

            Parameters: 
                g1(str): The gender of the first party
                g2(str): The gender of the second party
            Returns:
                str: Hetero, Same Sex or unkown
        ''' 
        sorted_gs = sorted([g1, g2])
        if sorted_gs in (['female', 'male'], ['male', 'mostly_female'], ['female', 'mostly_male'], ['mostly_female', 'mostly_male']):
            return "Hetero"
        elif sorted_gs in (['male', 'male'], ['female', 'female'], ['male', 'mostly_male'], ['female', 'mostly_female'], ['mostly_male', 'mostly_male'], ['mostly_female', 'mostly_female']):
            return "Same Sex"
        else:
            return "Unknown"


    def deal_with_parties(self, r):
        '''
            Handles parties.  Tries to split neatly into 1 Petitioner and 1 Respondent.   Handles exceptions to that
            Parameters:
                r(list(str)):  The record to be handled
            Returns:
                bool:  True if the record was parsed correctly
        '''
        for p in r['parties']:
            p["surname"], p["firstnames"], p["gender"] = self.split_and_get_gender(p)    

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
        r['Hetero'] = self.assign_hetero(r['resp_and_part'][0]['gender'], r['resp_and_part'][1]['gender'])
        return True

    def write_parties(self, parties):
        '''
            Writes the relevant fields of the parties to the spreadsheet

            Parameters: 
                parties (dict):  The dictionary of party info to written
            Returns: None
        ''' 
        for p in parties:
            for v in [list(p.values())[x] for x in [6, 5, 4, 1, 0]]:
                self.csv_file.write(','+v) 

    def get_decrees(self, events):
        '''
            Takes the list of events and returns on the divorce decrees
            Parameters: 
                events (list(dict)):  A list of the events 
            Returns: 
                list (dict):  Only the decrees
        ''' 
        decrees = [e for e in events if 'ORD:DECREE DIVORCE' in e['Description']]
        decrees = sorted(decrees, key=lambda x: datetime.strptime(x["Date"], '%m/%d/%Y').date())
        return decrees

    def write_decrees(self, decrees, max_decree_count):
        '''
            Prints the decrees to the csv file
            Parameters: 
                decrees (list(dict)):  A list of the divorce decrees
                max_decree_count:  The longest list of decrees in the entire recordset 
            Returns: 
                None
        '''         
        for e in decrees:
            url = e['&nbsp;']
            url = url.split('"')[1]
            url = url.split('"')[0]
            self.csv_file.write("," + self.convert_date(e["Date"]) + ',=HYPERLINK("' + 'https://public.traviscountytx.gov' + url + '")')
        for _ in range(max_decree_count-len(decrees)):    
            self.csv_file.write(",,")

    def write_fields(self, fields, r):
        '''
            Writes the specified fields of the record r to the csv file
            Parameters: 
                fields (list(str)): The list of fields to be written
                r (dict): The dictionary which will have the fields as keys
            Returns: 
                None
        ''' 
        for f in fields:
            self.csv_file.write("," + r[f])

    def run(self): 
        '''
            Opens the csv file and writes all the records
            Parameters: 
                None
            Returns: 
                None
        '''        
        with open ('csv/Records.csv', 'w') as self.csv_file:
            self.get_records()
            self.convert_dates()
            max_parties, max_decrees = self.write_headers()
            for r in self.records:
                if not (self.deal_with_parties(r)):
                    continue
                self.write_fields(self.pre_party_fields, r)
                self.write_parties(r['resp_and_part'])
                self.write_decrees(self.get_decrees(r['events']), max_decrees)
                self.write_fields(self.post_party_fields, r)
                self.write_parties(r['other_parties'])
                self.csv_file.write("\n")

if __name__ == "__main__": 
    csv_writer = CSVWriter()
    csv_writer.run()