from posixpath import split
import pandas as pd
import os
import re
import PyPDF2

list_comorbidities = ['Chronic kidney disease','CKD V','Hypertension','Urinary tract infection','Iron Deficiency' \
    'HTN','Chronic Obstructive Pulmonary Disease','COPD','chronic interstitial lung disease']
TOP_TABLETS = ['dexamethasone', 'pantoprazole', 'aciclovir', 'ecosprin', 'benadon', 'cyclophosphamide', 'thalidomide', 'febuxostat', 'lafutidine', 'amlodipine'] #by code
TOP_TABLETS = [tab.upper() for tab in TOP_TABLETS]
def read_myeloma_excel():
    df = pd.read_excel("C:\\Users\\prati\\Downloads\\Myeloma patients of Prantar.xlsx")
    df['Sex'] = df['Sex'].str.strip() 
    print(df['Sex'].value_counts())
    df2 = df.loc[df['Sex'].isin(["Male", "Female"])]
    print(df2.head(10))
    print(df2.count())
    print(df2.columns)
    return df2

def find_matched_files(df):
    pdf_dirs = ["C:\\Users\\prati\\Downloads\\patients_pdfs\\patients from 9th August 2019", "C:\\Users\\prati\\Downloads\\patients_pdfs\\Patients2"]
    pdf_files = [filename for foldr in pdf_dirs for filename in os.listdir(foldr) if filename.endswith(".pdf")]
    df['First Name'] = df['First Name'].astype(str)
    df['Last Name'] = df['Last Name'].astype(str)
    matched_files = []
    for index, row in df.iterrows():
        r = re.compile(row['First Name'].lower() + " " + row['Last Name'].lower()+"\s?\({0,1}[0-9]{0,1}\){0,1}"+"\.pdf")
        newlist = list(filter(r.match, pdf_files)) # Read Note below
        if newlist: 
            if 'ajit kumar das' in newlist:
                print("bug")
            # print(newlist)
            matched_files.extend(newlist)
        # file_name_from_df = row['First Name'].lower() + " " + row['Last Name'].lower()+".pdf"
        # if  file_name_from_df in pdf_files:
        #     print(file_name_from_df)
    print(matched_files)
    return matched_files
def extract_using_type2(extracted_txt, filename, directory):
    with open(os.path.join(directory,filename), 'r', errors='ignore') as fl:
        newlines1 = []
        newlines2 = []
        for line in fl.readlines():
            # print(line)
            line1 = re.sub(' +', ' ', line[:49]).strip()
            line2 = re.sub(' +', ' ', line[49:]).strip()
            if line1 != '' : newlines1.append(line1+"\n")
            if line2 != '' : newlines2.append(line2+"\n")
            
        # with open(os.path.join(dir_processed_txt,filename),"w") as file1:
        extracted_txt = ''
        extracted_txt = "".join(newlines1) + "".join(newlines1)
        # extracted_txt.writelines(newlines2)
    tmp_dict = {"file":filename}
    if any(x in extracted_txt.lower() for x in ['admission', 'hospitalisation']):
        tmp_dict["admission"] = 1      #true 
    else:
        tmp_dict["admission"] = 0
    name = re.search("(?<=Name:\s)(.*)(?=\n)", extracted_txt)
    if name:
        tmp_dict["Name"] = name.group().lower()
    age_sex = re.search("(?<=Age\/Sex:\s)([0-9]{1,3}y\s\/\s[MF])", extracted_txt)
    if age_sex:
        tmp_dict["age"] = age_sex.group()[:2]  
        tmp_dict["gender"] = age_sex.group()[-1]              
    date = re.findall("\d{2}-\d{2}-\d{4}", extracted_txt)
    if date:
        tmp_dict["date"] = date[0]
    office_id = re.search("(?<=Office ID:\s)(\d{4})", extracted_txt)
    if office_id:
        tmp_dict["office_id"] = office_id.group()
    blood_group = re.search("(?<=Blood Group:\s)([AB]{1,2}\+)", extracted_txt)
    if blood_group:
        tmp_dict["blood_group"] = blood_group.group()
    weight = re.search("(?<=Weight:\s)([0-9]{1,3})", extracted_txt)
    if weight:
        tmp_dict["Weight"] = weight.group()
    height = re.search("(?<=Height:\s)([0-9]{1,3})", extracted_txt)
    if height:
        tmp_dict["Height"] = height.group()
    # print(tmp_dict)
    bmi = re.search("(?<=BMI:\s)([0-9]{1,3}\.[0-9]{1,3})", extracted_txt)
    if bmi:
        tmp_dict["BMI"] = bmi.group()
    # print(tmp_dict)
    x = None
    if "Investigation results:" in extracted_txt and "Instructions:" in extracted_txt:
        # print(extracted_txt)
        x = re.search("(?<=Investigation results:)(.*)(?=Instructions:)", extracted_txt, re.DOTALL)
        # print(x)
    elif "Investigation results:" in extracted_txt and "Follow up:" in extracted_txt:
        x = re.search("(?<=Investigation results:)(.*)(?=Follow up:)", extracted_txt, re.DOTALL)
    # else:
    #     extracted_entities_by_page.append(tmp_dict)
    #     continue
    #     x = re.search("(?<=Notes:)(.*)(?=Rx)", pageObj.extractText())
    if x:
        extracted_Investigation = x.group()
        # print(extracted_Investigation) 
        matched_investigation = re.findall("((\w+\s?){1,3}:\s[0-9.%\/0-9]+\s(gm\/dL|gm\/dl|mg\/dl|mg\/dL|fl|fL|\/ul|\/uL|mmHg|Cms|million\/ul|mm\/hr|units\/L|mmHg|Cms.|Kg.|pg|%|kg\/m2|U\/L){0,1})", extracted_Investigation, re.DOTALL)

        for txt in matched_investigation:
            # print(txt[0])
            txt_temp= str.replace(txt[0], '\n',' ')
            single_test = txt_temp.split(':')
            tmp_dict[single_test[0].strip().upper().strip()] = single_test[1].split()[0]
    # print(tmp_dict)
    if "Notes:" in extracted_txt and "Vitals:" in extracted_txt:
        # print(extracted_txt)
        x = re.search("(?<=Notes:)(.*)(?=Vitals:)", extracted_txt, re.DOTALL)
        if x:
            extracted_notes = x.group()
            # tmp_dict['notes'] = extracted_notes
            matched_txt = re.findall("(([A-Z()]\w+\s+){1,3}[0-9.%\/0-9]+\s(gm\/dL|gm\/dl|mg\/dl|mg\/dL|fl|fL|\/ul|\/uL|mmHg|Cms|million\/ul|mm\/hr|units\/L|mmHg|Cms.|Kg.|pg|%|kg\/m2|U\/L){0,1})", extracted_notes)
            for txt in matched_txt:
                # print(txt[0])
                extracted_notes = extracted_notes.replace(txt[0], '')
                single_test = txt[0].split()
                if len(single_test) >= 3:
                    if len(single_test) == 4 and "Packed Cell Volume" in txt[0]:
                        tmp_dict[" ".join(single_test[:-1]).strip().upper().strip()] = single_test[-1].replace("%",'')
                    else:
                        tmp_dict[" ".join(single_test[:-2]).strip().upper().strip()] = single_test[-2]
            tmp_dict['notes'] = extracted_notes
    x_symptoms = None
    if "Symptoms:" in extracted_txt and "Findings:" in extracted_txt:
        # print(extracted_txt)
        x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Findings:)", extracted_txt, re.DOTALL)
    elif "Symptoms:" in extracted_txt and "Notes:" in extracted_txt:
        x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Notes:)", extracted_txt, re.DOTALL)
    if x_symptoms:
        extracted_symptoms = x_symptoms.group()
        tmp_dict['Symptoms'] = extracted_symptoms
    x_diagnosis = None
    if "Diagnosis:" in extracted_txt and "Investigation results:" in extracted_txt:
        x_diagnosis = re.search("(?<=Diagnosis:)(.*)(?=Investigation results:)", extracted_txt, re.DOTALL)
    # elif "Symptoms:" in extracted_txt and "Notes:" in extracted_txt:
    #     x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Notes:)", extracted_txt, re.DOTALL)
    if x_diagnosis:
        comordibity_found = ''
        extracted_diagnosis = x_diagnosis.group()
        for comordibity in list_comorbidities:
            if comordibity in extracted_diagnosis:
                extracted_diagnosis = extracted_diagnosis.replace(comordibity, '')
                comordibity_found += comordibity
        tmp_dict['Diagnosis'] = extracted_diagnosis
        tmp_dict['comorbidity'] = comordibity_found
        # print(tmp_dict['Diagnosis'])
    x_medical_history = None
    if "Medical History:" in extracted_txt and "Diagnosis:" in extracted_txt:
        x_medical_history = re.search("(?<=Medical History:)(.*)(?=Diagnosis:)", extracted_txt, re.DOTALL)
    # elif "Symptoms:" in extracted_txt and "Notes:" in extracted_txt:
    #     x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Notes:)", extracted_txt, re.DOTALL)
    if x_medical_history:
        extracted_medical_history = x_medical_history.group()
        tmp_dict['Medical History'] = extracted_medical_history
        # print(tmp_dict['Medical History'])
    x_medical_problems = None
    if "Medical Problems:" in extracted_txt and "Significant history:" in extracted_txt:
        x_medical_problems= re.search("(?<=Medical Problems:)(.*)(?=Significant history:)", extracted_txt, re.DOTALL)
    # elif "Symptoms:" in extracted_txt and "Notes:" in extracted_txt:
    #     x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Notes:)", extracted_txt, re.DOTALL)
    if x_medical_problems:
        extracted_medical_problems = x_medical_problems.group()
        tmp_dict['Medical Problems'] = extracted_medical_problems
    x_significant_history = None
    if "Significant history:" in extracted_txt and "Diagnosis:" in extracted_txt:
        x_significant_history = re.search("(?<=Significant history:)(.*)(?=Diagnosis:)", extracted_txt, re.DOTALL)
    # elif "Symptoms:" in extracted_txt and "Notes:" in extracted_txt:
    #     x_symptoms = re.search("(?<=Symptoms:)(.*)(?=Notes:)", extracted_txt, re.DOTALL)
    if x_significant_history:
        extracted_significant_history = x_significant_history.group()
        tmp_dict['Significant History'] = extracted_significant_history
    matched_tablets = re.findall("Tablet (\w+)", extracted_txt)
    tablets = "\n".join(matched_tablets)
    print(tablets)
    tmp_dict['tablets'] = tablets

    tmp_dict.pop('On', None)
    tmp_dict.pop('INR', None)
    tmp_dict.pop('Test', None)
    tmp_dict.pop('Inj', None)
    tmp_dict.pop('Dec', None)    
    tmp_dict.pop('Has', None)
    return tmp_dict      


def extract_using_type1(txt, filename):
    tmp_dict = {"file":filename}
    if any(x in txt.lower() for x in ['admission', 'hospitalisation']):
        tmp_dict["admission"] = 1      #true 
    else:
        tmp_dict["admission"] = 0
    # print(txt)
    ''' extracting patient details'''
    tmp_dict["Name"] = filename.split(".")[0]
    if tmp_dict['Name'][-1] in ['1','2','3','4','5','6','7','8','9']:
        tmp_dict['Name'] = tmp_dict['Name'][:-1] 
    elif tmp_dict['Name'][-1] in [')']:
        tmp_dict['Name'] = tmp_dict['Name'][:-4] 

    if "Male" in txt:
        tmp_dict["gender"] = "M"
    else:
        tmp_dict["gender"] = "F"
    age = re.findall("\d{1,2}y", txt)
    if age:
        tmp_dict["age"] = age[0][:-1]
    date = re.findall("\d{2}-\d{2}-\d{4}", txt)
    if date:
        tmp_dict["date"] = date[0]
    office_id = re.search("(?<=ID No.\s)(\d{4})", txt)
    if office_id:
        tmp_dict["office_id"] = office_id.group()
    # print(tmp_dict)
    '''extracting notes and test reports if mentioned in notes'''
    if "Investigations:" in txt:
        x = re.search("(?<=Notes:)(.*)(?=Investigations:)", txt, re.DOTALL)
    else:
        x = re.search("(?<=Notes:)(.*)(?=Rx)", txt, re.DOTALL)
    if x:
        notes = x.group()
    else:
        return tmp_dict
    # print(notes) 
    tmp_dict["notes"] =  notes
    '''replacing 2 numbers by adding . between then'''
    two_nos = re.findall("\d+[ ,]\d+", notes)
    for two_no in two_nos:
        notes = notes.replace(two_no, ".".join(re.split(" |,", two_no)))
    # print(notes)
    matched_txt = re.findall("((\w+\s+){1,3}[0-9.%\/0-9]+\s(gm\/dL|gm\/dl|mg\/dl|mg\/dL|fl|fL|\/ul|\/uL|mmHg|Cms|million\/ul|million\/uL|mm\/hr|units\/L|mmHg|Cms.|Kg.|pg|%|kg\/m2|mmol\/L){0,1})", notes, re.DOTALL)
    if not matched_txt:
        print(filename)
        probable_test_name_values = notes.split(',')
        for item in probable_test_name_values:
            if '-' in item:
                values = item.split('-')
                if len(values) == 2:
                    notes = notes.replace(item, '')
                    tmp_dict[values[0].upper().strip()] = values[1]
    for mtxt in matched_txt:                
        # print(mtxt[0])
        notes = notes.replace(mtxt[0], '')
        single_test = mtxt[0].split()
        if len(single_test) >= 3:
            if len(single_test) == 4 and "Packed Cell Volume" in mtxt[0]:
                tmp_dict[" ".join(single_test[:-1]).upper().strip()] = single_test[-1].replace("%",'')
            else:
                tmp_dict[" ".join(single_test[:-2]).upper().strip()] = single_test[-2]
    
    matched_tests_2nd = re.findall("([a-zA-Z :]+-[0-9.]+)", notes, re.DOTALL) #, Sugar Fasting-107.0 Sugar PP-78.0,, Calcium-8.85 SGOT-12,,,,,,, A:G Ratio-2.0 (05-05-20)
    for item in matched_tests_2nd:
        values = item.split('-')
        if len(values) == 2:
            notes = notes.replace(item, '')
            tmp_dict[values[0].upper().strip()] = values[1]


    tmp_dict["notes"] =  notes
    matched_tablets = re.findall("TAB (\w+)", txt)
    tablets = "\n".join(matched_tablets)
    # print(tablets)
    tmp_dict['tablets'] = tablets
    x_reason = None
    if "Reason for Visit:" in txt and "Notes:" in txt:
        x_reason = re.search("(?<=Reason for Visit:)(.*)(?=Notes:)", txt, re.DOTALL)
    if x_reason:
        extracted_reason = x_reason.group()
        tmp_dict['Reason for Visit'] = extracted_reason

        comordibity_found = ''
        for comordibity in list_comorbidities:
            if comordibity in extracted_reason or comordibity.lower() in extracted_reason:
                # extracted_diagnosis = extracted_diagnosis.replace(comordibity, '')
                comordibity_found += comordibity
        # tmp_dict['Diagnosis'] = extracted_diagnosis
        tmp_dict['comorbidity'] = comordibity_found    
    return tmp_dict
def create_csv(matched_files):
    type = 5
    if type == 5:
        extracted_entities_by_page = []
        dir_processed_txt = ["C:\\Users\\prati\\Downloads\\patients from 9th August 2019 txt", "C:\\Users\\prati\\Downloads\\p2_txt", "C:\\Users\\prati\\Downloads\\p3_txt"]
        for dir in dir_processed_txt:
            for filename in os.listdir(dir):
                if filename.endswith(".txt") and filename[:-4] in matched_files:# and filename == "chandan mukhopadhyay.pdf.txt": 
                    with open(os.path.join(dir,filename), 'r', errors='ignore') as fl:
                        txt = fl.read() 
                          
                        if "Office ID" in txt:
                            tmp_dict = extract_using_type2(txt, filename, dir)
                        else:
                            tmp_dict = extract_using_type1(txt, filename)
                        #adding tablets binary col
                        if "tablets" in tmp_dict:
                            for item in TOP_TABLETS:
                                if item in tmp_dict['tablets']:
                                    tmp_dict["TAB_"+item] = 1
                        if "comorbidity" in tmp_dict:
                            for item in list_comorbidities:
                                if item in tmp_dict['comorbidity']:
                                    tmp_dict[item] = 1    
                        tmp_dict.pop('ACID', None)
                        tmp_dict.pop('ADMISSION AND DISCHARGE DATE', None)
                        tmp_dict.pop('RATIO', None)
                        tmp_dict.pop('TOTAL', None)
                        tmp_dict.pop('tablets', None)    
                        tmp_dict.pop('comorbidity', None)   
                        tmp_dict.pop('HAS', None)    
                        extracted_entities_by_page.append(tmp_dict)
                        # print(extracted_entities_by_page)
                        # print("-"*100)
    df = pd.DataFrame(extracted_entities_by_page) 
    df = df.drop('PROTHROMBIN', 1)
    print(len(df.columns))
    print(df.columns)
    df['ALKALINE PHOSPHATASE'].fillna(df.ALP, inplace=True)
    df['FASTING BLOOD GLUCOSE'].fillna(df.FBS, inplace=True)
    df['FASTING BLOOD GLUCOSE'].fillna(df['SUGAR (F)'], inplace=True)
    df['FASTING BLOOD GLUCOSE'].fillna(df['SUGAR(F)'], inplace=True)
    df['BLOOD GLUCOSE PP'].fillna(df['PPBS'], inplace=True)
    df['BLOOD GLUCOSE PP'].fillna(df['SUGAR(PP)'], inplace=True)
    df['TOTAL PROTEIN'].fillna(df.PROTEIN, inplace=True)
    df['TOTAL PROTEIN'].fillna(df['TOTAL PROTEINS'], inplace=True)
    df['TOTAL PROTEIN'].fillna(df['TP'], inplace=True)
    df.PLATELET.fillna(df['PLATELET COUNT'], inplace=True)
    df.PLATELET.fillna(df['PLT'], inplace=True)
    df['PACKED CELL VOLUME'].fillna(df.PCV, inplace=True)
    df.RBC.fillna(df['RBC COUNT'], inplace=True)
    df.GLOBULIN.fillna(df.GLB, inplace=True)
    df.ALBUMIN.fillna(df.ALB, inplace=True)
    df.HEMOGLOBIN.fillna(df.HB, inplace=True)
    # df.HEMOGLOBIN.fillna(df.HB, inplace=True)
    # df.HEMOGLOBIN.fillna(df.HB, inplace=True)

    # df['FASTING BLOOD GLUCOSE'].str.cat(df['FBS']).str.cat(df['SUGAR(F)']).str.cat(df['SUGAR (F)'])
    df.HEMOGLOBIN.fillna(df.HB, inplace=True)
    df.drop(['ALP', 'FBS', 'PLATELET COUNT', 'PCV', 'RBC COUNT', 'GLB', 'ALB', 'HB', 'PLT', 'SUGAR (F)', 'SUGAR(F)', 'PPBS', 'SUGAR(PP)', 'PROTEIN', 'TOTAL PROTEINS', \
        'TP'], axis=1, inplace=True)
    
  
    df = df.dropna(thresh=df.shape[0]*0.02,how='all',axis='columns')
    print(len(df.columns))
    print(df.columns)
    # df['date'] = pd.to_datetime(df['date'])#, format="%d/%m/%Y")
    # df = df.drop_duplicates(subset=['date', 'office_id'], keep='first').sort_values([ "Name"])#, 'date'])
    df = df.sort_values([ "Name"])#, 'date'])
    # df = df.sort_index(axis=1)
    df.to_excel("C:\\Users\\prati\\Downloads\\patient_data_apr4_v3.xlsx", encoding='utf-8', index=False)
    # all_tablets = " ".join(df['tablets'].str.cat(sep=' ').split('\n')).lower().split()
    # print(all_tablets)
    # from collections import Counter
    # print(Counter(all_tablets))
if __name__ == "__main__":
    df_myeloma = read_myeloma_excel()
    matched_files = find_matched_files(df_myeloma)
    create_csv(matched_files)
