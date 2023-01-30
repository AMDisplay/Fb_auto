import csv
import json
import os

filename = 'csv\Ready_analysis.jaon'


with open("csv\For_analysis.json", encoding="windows-1251") as r_file:
    file_reader = json.loads(r_file.read())
    for acc in file_reader:
        if acc['status'] == "Success" or acc['status'] == "Sms ne prishla":
            country = acc['country_number']
            operator = acc['operator_number']
            ip = acc['payload']['user_proxy_config']['proxy_host']
            data = {
                    'status' : acc['status'],
                    'ip': ip,
                    "country_number": country,
                    "operator_number": operator
                        }
            if os.stat(filename).st_size == 0:
                with open(filename, "w") as file:
                    json.dump([data], file, indent=4)
            else:
                with open(filename) as fp:
                    listObj = json.loads(fp.read())
                    listObj.append(data)
                with open(filename, 'w') as json_file:
                    json.dump(listObj, json_file, 
                                        indent=4,  
                                        separators=(',',': '))
