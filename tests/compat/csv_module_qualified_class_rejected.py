# expect: error not yet supported by C++ code generation
import csv
import io

def main():
    src = io.StringIO("a,b\n1,2\n")
    for row in csv.DictReader(src):
        print(row["a"])

main()
