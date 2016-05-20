import csv

with open('foodlist.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print (row['ndb_number'], row['food'])

