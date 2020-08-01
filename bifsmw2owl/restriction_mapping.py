import rdflib
import json
import argparse

URI_TMP = 'https://wba-initiative.org/noprefix/'


def main(argv):
    # load graph
    g = rdflib.Graph()
    g.parse(args.input, publicID=URI_TMP, format="xml")

    qres = g.query(
        """SELECT ?class ?p ?v
        WHERE {
        ?class rdfs:subClassOf _:b.
        _:b rdf:type owl:Restriction.
        _:b owl:onProperty ?p.
        _:b ?v ?o.
        filter (?v in (owl:someValuesFrom, owl:hasValue, owl:allValuesFrom)) # only take someValuesFrom, allValuesFrom, hasValue
        }
        """)

    mapping = {}

    for res in qres:
        clss = str(res[0])
        p = str(res[1]).strip(
            "/")  # URI in bifd.owl ends with / such as :  https://wba-initiative.org/bifd/inputCircuit/
        v = str(res[2])
        if clss not in mapping.keys():
            mapping[clss] = {}
        mapping[clss][p] = v

    with open(args.output, "w") as f:
        json.dump(mapping, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="name of input file")
    parser.add_argument("-o", "--output", help="name of output file")
    args = parser.parse_args()
    main(args)
