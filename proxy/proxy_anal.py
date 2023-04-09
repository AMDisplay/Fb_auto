import json
import os

# Для Анализа полученных акков и фильтраций по успешным и не пришедшим смс

filename = 'csv\Ready_analysis.json'
# 21
success = []
all_try = []
with open("csv\For_analysis.json", encoding="windows-1251") as r_file:
    file_reader = json.loads(r_file.read())
    sum_reg_acc = len(file_reader)
    print('Сумма попыток = %s', sum_reg_acc)
    for acc in file_reader:
        if acc['status'] == "Success" or acc['status'] == "Sms ne prishla":
            if acc['status'] == "Success":
                success.append(acc)
            else:
                all_try.append(acc)
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

prohod_succees = len(all_try)/len(success)
print('Количество пройденных = %s, из них количество успешных = %s', len(all_try), len(success))
print('Процент прохода %s', prohod_succees)
open("csv\For_analysis.json","w").close()
