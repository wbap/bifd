import rdflib
import argparse
import re

URI_TMP = 'https://wba-initiative.org/noprefix/'
BIFD_PREFIX = 'https://wba-initiative.org/bifd/'
WBRA_PREFIX = 'https://wba-initiative.org/wbra/'

def main(argv):
    # load graph
    g = rdflib.Graph()
    g.parse(args.input, publicID=URI_TMP, format="xml")

    # create mapping for URI
    qres4 = g.query(
        """SELECT ?s
        WHERE {
        ?s rdf:type owl:Class.
        ?s ?p ?o.
        filter (strstarts(str(?s), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3A"))
        }
        """)

    qres5 = g.query(
        """SELECT ?target
        WHERE {
        {
        ?target ?p ?o.
        filter (strstarts(str(?target), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3A") &&
        !strstarts(str(?target), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3A") )
        }
        UNION
        {
        ?s ?p ?target.
        filter (strstarts(str(?target), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3A") &&
        !strstarts(str(?target), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3A") )
        }
        }
        """
    )

    qres6 = g.query(
        """SELECT ?o
        WHERE {
        ?s ?p ?o.
        filter (strstarts(str(?o), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/") &&
         !strstarts(str(?o), "http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category") ) 
        } 
        """
    )

    # keep only subclasses of BIF:Circuit, BIF:UniformCircuit, BIF:Connection
    # but exclude BIF:Circuit, BIF:UniformCircuit, BIF:Connection themselves
    qres7 = g.query(
        """SELECT ?s
        WHERE {
        ?s rdfs:subClassOf ?o.
        filter (?o in (URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3ACircuit"),
        URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3AUniformCircuit"),
        URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3AConnection")))
        filter (?s not in (URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3ACircuit"),
        URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3AUniformCircuit"),
        URI("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3AConnection"))) 
        }
        """
    )

    mapping = {}

    for row in qres4:
        k = str(row[0])
        v = k.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3ABIF-3A",
                      BIFD_PREFIX)
        mapping[k] = v

    for row in qres5:
        k = str(row[0])
        v = k.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/Category-3A",
                      WBRA_PREFIX)
        mapping[k] = re.match('.*/',v).group() + re.sub('.*/','',v).replace('-2D','-') if re.match('.*/',v) else v

    for row in qres6:
        k = str(row[0])
        v = k.replace("http://183.181.89.140/mediawiki/index.php/Special:URIResolver/",
                      BIFD_PREFIX)
        mapping[k] = v

    keep_s = set()
    for row in qres7:
        keep_s.add(str(row[0]))

    with open(args.output, "w") as fout:
        for k, v in mapping.items():
            if k in keep_s:
                fout.write("{}\t{}\n".format(k, v))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="name of input file")
    parser.add_argument("-o", "--output", help="name of output file")
    args = parser.parse_args()
    main(args)