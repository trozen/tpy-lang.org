# expect: error Module 'csv' has no function 'DictReader'
import csv
import io

def main():
    src = io.StringIO("a,b\n1,2\n")
    for row in csv.DictReader(src):
        print(row["a"])

main()
