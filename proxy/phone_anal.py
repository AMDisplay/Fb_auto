import json
import os

filename = 'csv\Ready_analysis.jaon'

# Айпи определяется статусом успех или смс не пришла
# номер определятся только статусом успех

# 31
# 25 "'216.52.25.27
# 24 '66.23.206.158'
# 5 172.96.166.126':
# 32   '64.74.163.147':

success = []
with open("csv\Ready_analysis.json") as r_file:
    country = {}
    file_reader = json.loads(r_file.read())
    sum_reg_acc = len(file_reader)
    print('Сумма успешных прокси = %s', sum_reg_acc)
    a = 0
    b = 0
    c = 0
    d = 0
    e = 0
    operatorcanada = []
    operatorsenegal = []
    operatoregypt = []
    operatornicaragua = []
    operatormongolia = []
    operatorcongo = []
    operatorhaiti = []
    operatorengland = []
    operatorcolombia = []
    operatortanzania = []
    operatormauritius = []
    
    for acc in file_reader:
        # print(acc)
        if acc['status'] == "Success":
            # print(acc)
            success.append(acc)
            if acc['country_number'] == 'canada':
                operatorcanada.append(acc['operator_number'])
                country[acc['country_number']] = operatorcanada
                
            elif acc['country_number'] == 'senegal':
                operatorsenegal.append(acc['operator_number'])
                country[acc['country_number']] = operatorsenegal
            elif acc['country_number'] == 'egypt':
                operatoregypt.append(acc['operator_number'])
                country[acc['country_number']] = operatoregypt
            elif acc['country_number'] == 'nicaragua':
                operatornicaragua.append(acc['operator_number'])
                country[acc['country_number']] = operatornicaragua
            elif acc['country_number'] == 'mongolia':
                operatormongolia.append(acc['operator_number'])
                country[acc['country_number']] = operatormongolia
            elif acc['country_number'] == 'congo':
                operatorcongo.append(acc['operator_number'])
                country[acc['country_number']] = operatorcongo
            elif acc['country_number'] == 'haiti':
                operatorhaiti.append(acc['operator_number'])
                country[acc['country_number']] = operatorhaiti
            elif acc['country_number'] == 'england':
                operatorengland.append(acc['operator_number'])
                country[acc['country_number']] = operatorengland
            elif acc['country_number'] == 'colombia':
                operatorcolombia.append(acc['operator_number'])
                country[acc['country_number']] = operatorcolombia
            elif acc['country_number'] == 'tanzania':
                operatortanzania.append(acc['operator_number'])
                country[acc['country_number']] = operatortanzania
            elif acc['country_number'] == 'mauritius':
                operatormauritius.append(acc['operator_number'])
                country[acc['country_number']] = operatormauritius
    
    # for value in country.items():
    #     print(value[0])
    #     print(len(value[1]))
    print(country)
    print('Сумма успешных %s', len(success))
    # print(a) 
    # print(b)
    # print(c)
    # print(d)
    # print(e)
