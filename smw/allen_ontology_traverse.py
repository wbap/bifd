# This script extracts id, whether leaf, acronym, and name from an ontology json file from Allen's connectome project.
# Use: python allen_ontology_traverse.py infile.json outfile.txt
# 
import sys
import json

def traverse(children, result):
    for child in children:
        leaf = not ("children" in child and len(child["children"])>0)
        result += "{}\t{}\t{}\t{}\n".format(child["id"],leaf,child["acronym"],child["name"])
        if "children" in child:
            result = traverse(child["children"], result)
    return result

def main():
    args = sys.argv
    a = open(args[1])
    b = json.load(a)
    msg = b["msg"]
    res = ""
    res = traverse(msg, res)
    with open(args[2],'w') as f:
        print("%s" % res, file=f)

if __name__ == "__main__":
    main()
