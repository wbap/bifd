# This script joins two text files.
# Use: python join.py infile1 infile2 key_pos field_separator > outfile
#      key_pos is the key position (1 origin) in infile1.
#      A record of infile2 may be joined after each record of infile1,
#      if the first item of the record (infile2) matches the key item.
#      field_separator is "\t" by default.
# 
import sys

def main():
    args = sys.argv
    if len(args) < 4:
       print(len(args))
       print("Use: python join.py infile1 infile2 key_pos (field_separator)", file=sys.stderr)
       sys.exit(1)
    if len(args) == 4:
        field_separator = '\t'
    else:
        field_separator = args[4]
    key_pos = int(args[3]) - 1
    if key_pos < 0:
        print("key_pos must be a positive integer.", file=sys.stderr)
        sys.exit(1)
    infile2 = open(args[2])
    line = infile2.readline()
    dct = {}
    while line:
        line = line.rstrip("\n")
        buf = line.split(field_separator)
        dct[buf[0]] = buf
        line = infile2.readline()
    infile2.close
    infile1 = open(args[1])
    line = infile1.readline()
    while line:
        line = line.rstrip("\n")
        buf = line.split(field_separator)
        if buf[key_pos] in dct:
            for x in dct[buf[key_pos]][1:]:
                line += field_separator + x
            print(line)
        else:
            print(line)
        line = infile1.readline()
    infile1.close

if __name__ == "__main__":
    main()
