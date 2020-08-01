import rdflib
import argparse

URI_TMP = 'https://wba-initiative.org/noprefix/'

def main(argv):
    # load graph
    g = rdflib.Graph()
    g.parse(args.input, publicID=URI_TMP, format="xml")

    # create mapping for URI
    qres4 = g.query(
        """SELECT ?p
        WHERE {
        ?s ?p ?o.
        filter (strstarts(str(?p), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3ABIF-3A"))
        }
        """)

    mapping = {}

    for row in qres4:
        k = str(row[0])
        v = k.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3ABIF-3A",
                      "https://wba-initiative.org/bifd/")
        mapping[k] = v

    with open(args.output, "w") as fout:
        for k, v in mapping.items():
            fout.write("{}\t{}\n".format(k, v))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="name of input file")
    parser.add_argument("-o", "--output", help="name of output file")
    args = parser.parse_args()
    main(args)