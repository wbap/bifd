# coding=utf-8
import rdflib
from rdflib import RDFS
from rdflib import RDF
from rdflib import OWL, XSD
from rdflib import URIRef, Literal
from rdflib import BNode
import re
import argparse

URI_TMP = 'https://wba-initiative.org/noprefix/'
BIFD_PREFIX = 'https://wba-initiative.org/bifd/'

def load_dict(fname):
    convert_uris = {}
    with open(fname) as f:
        for line in f:
            k, v = line.strip().split("\t")
            convert_uris[k] = v
    return convert_uris

def main(args):
    # load graph
    g = rdflib.Graph()
    g.parse(args.input, publicID=URI_TMP, format="xml")

    # Tripleを含まないgraphをファイルから作成し、そこにTripleを追加していく
    g2 = rdflib.Graph()
    g2.parse(args.header, publicID=URI_TMP, format="xml")

    # bifd.owl
    g3 = rdflib.Graph()
    g3.parse(args.bifd, publicID=URI_TMP, format="xml")

    convert_uris = load_dict(args.subject)
    convert_ps = load_dict(args.predicate)
    convert_ps["https://wba-initiative.org/bifd/label"] = str(RDFS.label)

    # 処理対象のクラスの抽出 このうちのs.tsvに記載のあるものしか最終出力に含めない
    query_class = g.query(
        """SELECT ?class
        WHERE {
        ?class rdf:type owl:Class.
        }
        """)

    keep_s = set()

    for c in query_class:
        keep_s.add(c[0])

    query_references = g.query(
        """SELECT ?uri ?p ?v 
        WHERE {
        ?uri rdf:type swivt:Subject.
        ?uri ?p ?v.
        filter (?p in (property:BibTex-3Ahas_doi, URI("https://wba-initiative.org/noprefix/URLhas"), rdfs:label))
        filter (strstarts(str(?uri), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/-2A"))
        } 
        """)

    references = {}
    references_val = {}
    references_s_o = {}

    for x in query_references:
        p = str(x[1])
        if x[0] not in references:
            references[x[0]] = [p]
        else:
            references[x[0]].append(p)
        references_val["{}\t{}".format(str(x[0]), str(x[1]))] = str(x[2])
    for k in references.keys():
        predicates = []
        for p in references[k]:
            predicates.append(p)
        if "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3ABibTex-3Ahas_doi" in predicates:
            o = references_val["{}\t{}".format(str(k), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3ABibTex-3Ahas_doi")]
            references_s_o[str(k.split("/")[-1])] = o
            continue
        if "https://wba-initiative.org/noprefix/URLhas" in predicates:
            o = references_val["{}\t{}".format(str(k), "https://wba-initiative.org/noprefix/URLhas")]
            references_s_o[str(k.split("/")[-1])] = o
            continue
        if str(RDFS.label) in predicates:
            o = references_val["{}\t{}".format(str(k), str(RDFS.label))]
            references_s_o[str(k.split("/")[-1])] = o
            continue
        if True:
            print("Error: no info for references provided.")
            exit(1)
    obo_id_dict = {}

    for s, p, o in g:
        if s not in keep_s:
            continue
        if str(s) in convert_uris.keys():
            s = URIRef(convert_uris[str(s)])
        if str(o) in convert_uris.keys():
            o = URIRef(convert_uris[str(o)])
        if str(p) in convert_ps.keys():
            p = URIRef(convert_ps[str(p)])
        if str(p) == "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3AOBO_ID":
            obo_id_dict[str(s)] = str(o)
        if str(s) in convert_uris.values() and (p == RDFS.subClassOf or p == RDFS.label or str(p).startswith(BIFD_PREFIX) or o == OWL.Class):
            g2.add((s, p, o))

    for s, p, o in g:
        if s not in keep_s:
            continue
        if str(s) in convert_uris.keys():
            s = URIRef(convert_uris[str(s)])
        if str(p) == "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Property-3AOBO_ID":
            if str(s) in obo_id_dict.keys():
                reg = re.compile(r'^[a-zA-Z_][\w.-]*$')
                if reg.match(obo_id_dict[str(s)]): # check if it results in a valid uri
                    if str(s) in convert_uris.values():
                        g2.add((s, OWL.sameAs, URIRef("http://purl.obolibrary.org/obo/{}".format(obo_id_dict[str(s)]))))

    query_object_property = g3.query(
        """SELECT ?op
        WHERE {
        ?op rdf:type owl:ObjectProperty.
        }""")

    object_properties = set()
    for res in query_object_property:
        p = str(res[0]).strip("/")
        object_properties.add(p)
    for s, p, o in g2:
        if str(p) == 'https://wba-initiative.org/bifd/reference':
            k = o.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/", '')
            if k in references_s_o.keys():
                g2.add((s, p, Literal(references_s_o[k], datatype=XSD.string)))
            g2.remove((s, p, o))

        if str(p) == 'https://wba-initiative.org/bifd/taxon':
            g2.add((s, p, Literal("http://purl.obolibrary.org/obo/{}".format(obo_id_dict[str(o)]), datatype=XSD.string)))

        if str(p) in convert_ps.values() and p != RDFS.label and str(p) in object_properties:  # プロパティの制約条件の変換
            if str(p) == "https://wba-initiative.org/bifd/transmitter" or str(p) == "https://wba-initiative.org/bifd/modType":
                continue
            g2.remove((s, p, o))
            blank_node = BNode()
            g2.add((s, RDFS.subClassOf, blank_node))
            g2.add((blank_node, RDF.type, OWL.Restriction))
            g2.add((blank_node, OWL.onProperty, p))
            g2.add((blank_node, OWL.someValuesFrom, o))

    for s, p, o in g2:
        if o.startswith("http://183.181.89.140/mediawiki/index.php/Special:URIResolver"):
            g2.remove((s, p, o))
            # s.tsvに含まれる変換対象のURIではない、oのURIの変換を正規表現ベースでやる
            o = URIRef(o.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3A",
                             "https://wba-initiative.org/bifd/") \
                   .replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3A",
                            "http://wba-initiative.org/wbra/")
            # Glutamateは特別扱い
            .replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Glutamate", "https://wba-initiative.org/bifd/Glutamate"))
            g2.add((s, p, o))

    g2.serialize(args.output, publicID=URI_TMP, format="pretty-xml")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="name of input file")
    parser.add_argument("-d", "--header", help="name of header file")
    parser.add_argument("-s", "--subject", help="name of uri mapping file")
    parser.add_argument("-p", "--predicate", help="name of predicate mapping file")
    parser.add_argument("-o", "--output", help="name of output file")
    parser.add_argument("-b", "--bifd", help="name of bifd file")
    args = parser.parse_args()
    main(args)