
import os

filename = 'csv\email.txt'
new_filename = 'csv\\new_email.txt'


def qwe():
    if os.stat(filename).st_size == 0:
        print('email text end')
    else:
        with open(filename) as fp:
            email = fp.readline()


    with open(filename) as infile, open(new_filename, "w",) as outfile:
        for line in infile:
            if email not in line:
                outfile.write(line)
    os.remove(filename)
    os.rename(new_filename, filename)
    return email


email = qwe()
email = email.split(":")
