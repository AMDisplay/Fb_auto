import csv

with open("csv\For_analysis.csv", encoding="windows-1251") as r_file:
    file_reader = r_file.read().splitlines()
    for row in file_reader:
        row = row.split('\t')
        if row[1] == "Success":
            country = row[-2]
            operator = row[-1]
            first = row[6].split(",")
            second = first[12]
            ip = second[16:]
            with open('csv\Ready_analysis.csv',  'a', newline='') as ready_analysis:
                colums = ['status', 'ip', "country_number", "operator_number"]
                account = {
                        'status': row[1],
                        'ip': ip,
                        "country_number": country,
                        "operator_number": operator
                    }
                writer = csv.DictWriter(
                    ready_analysis,
                    fieldnames=colums,
                    delimiter=';')
                writer.writerow(account)
        elif row[1] == "Sms ne prishla":
            country = row[-2]
            operator = row[-1]
            first = row[6].split(",")
            second = first[12]
            ip = second[16:]
            with open('csv\Ready_analysis.csv',  'a', newline='') as ready_analysis:
                colums = ['status', 'ip', "country_number", "operator_number"]
                account = {
                        'status': row[1],
                        'ip': ip,
                        "country_number": country,
                        "operator_number": operator
                    }
                writer = csv.DictWriter(
                    ready_analysis,
                    fieldnames=colums,
                    delimiter=';')
                writer.writerow(account)