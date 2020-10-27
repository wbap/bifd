from itertools import chain

import rdflib
from rdflib import RDFS
from graphviz import Digraph
from rdflib import OWL
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input file", type=str)
parser.add_argument("output", help="output file", type=str)
parser.add_argument("bifd", help="bifd.owl", type=str)
args = parser.parse_args()

URI_TMP = 'https://wba-initiative.org/noprefix/'

g = rdflib.Graph()
g.parse(args.input, publicID=URI_TMP, format="xml")
g_bifd = rdflib.Graph()
g_bifd.parse(args.bifd, publicID=URI_TMP, format="xml")

dg = Digraph(engine="fdp", format="svg")
dg.attr(compound='true')

query_datatype_prop = g_bifd.query(
    """
    SELECT ?s
    WHERE {
    ?s rdf:type owl:DatatypeProperty.
    } 
    """
)

datatype_props = set()
for s in query_datatype_prop:
    datatype_props.add(str(s[0]))

tooltip_text = defaultdict(set)

for s, p, o in g:
    s = s.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if str(p) not in datatype_props:
        continue
    tooltip_text[str(s)].add(str(p).split("/")[-1] + ":" + str(o))

query_sub = g.query(
    """SELECT ?s ?p
    WHERE {
    ?s rdfs:subClassOf ?p.
    }
    """
)

for sub, prnt in query_sub:
    sub = sub.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if "/" in str(prnt): # これを含まないものはRestrictionなどのnode
        tooltip_text[str(sub)].add("subClassOf:" + str(prnt).split("/")[-1])
query = g.query(
    """SELECT ?s ?p ?o ?v
    WHERE {
    ?s rdfs:subClassOf ?b.
    ?b rdf:type owl:Restriction.
    ?b owl:onProperty ?p.
    ?b ?v ?o.
    filter (?v in (owl:someValuesFrom, owl:allValuesFrom))
    } 
    """
)

uri_name=defaultdict(set)
for s, p, o in g:
    s = s.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if p == RDFS.label:
        uri_name[s].add(o)

# まず最初にループを回してhasPartを持つnodeとその終端を特定 これらはclusterとして作成しなければいけないため
cluster_dict=defaultdict(set)
for s, prop, range, constraint in query:
    s = s.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    range = range.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if prop.split("/")[-1] == "hasPart":
        cluster_dict[s].add(range)
first_parent = defaultdict(str)
for k in cluster_dict.keys():
    for v in cluster_dict[k]:
        if v in cluster_dict.keys():
            continue
        if v not in first_parent.keys():
            first_parent[v] = k

for k in cluster_dict.keys():
    with dg.subgraph(name="cluster_{}".format(k)) as c: # subgraphに対してtooltip表示できない
        c.attr(color='blue')
        c.attr(label=';'.join(uri_name[k])) # RDFS.labelにする
        for v in cluster_dict[k]:
            if v in cluster_dict.keys():
                dg.edge("cluster_{}".format(k), "cluster_{}".format(v), color='blue') # clusterの場合
            else:
                if first_parent[v] == k:
                    with c.subgraph(name=v) as subsub:
                        subsub.node(v, ';'.join(uri_name[v]))
                else:
                    dg.edge("cluster_{}".format(k), v, color='blue')

for s in chain(g.subjects(), g.objects()):
    s = s.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if s not in cluster_dict.keys():
        if s in uri_name.keys():
            name = ";".join(uri_name[s])
        else:
            if "wba-initiative.org" in str(s):
                name = str(s).split("/")[-1]
            else:
                continue
        tooltip = " ".join(tooltip_text[str(s)])
        shape = "ellipse"
        if "subClassOf:Connection" in tooltip:
            name = ""
            tooltip = ""
        elif "subClassOf:Circuit" in tooltip:
            shape = "box"
        else:
            continue
        if str(s) in tooltip_text.keys() and len(tooltip) > 0:
            dg.node(str(s), name, tooltip=tooltip, shape=shape)
        else:
            dg.node(str(s), name, shape=shape, width = "0.1", height = "0.1")


query_object_prop = g_bifd.query(
    """
    SELECT ?s
    WHERE {
    ?s rdf:type owl:ObjectProperty.
    } 
    """
)

object_props = set()
for s in query_object_prop:
    object_props.add(str(s[0]))

for s, prop, range, constraint in query:
    if constraint == OWL.someValuesFrom:
        tail_symbol = "&#8707;"
    elif constraint == OWL.allValuesFrom:
        tail_symbol = "&#8704;"
    s = s.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    range = range.replace("https:", "").replace("http:", "")  # DOT形式で:は危険
    if str(prop) not in object_props:
        continue
    prop_name = prop.split("/")[-1]
    if range in cluster_dict.keys():
        range = "cluster_{}".format(range)
    if s in cluster_dict.keys():
        s = "cluster_{}".format(s)
    if prop_name != "hasPart":
        if prop_name == "inputCircuit": # inputCircuitの場合は矢印のむきを入れ替える
            tmp = range
            range = s
            s = tmp
        # label=prop_nameとしてedgeにラベルつけるのはやめる　見づらくなるため
        # headlabel=tail_symbolもやめる
        dg.edge(str(s), str(range), label="", headlabel="", arrowhead="vee", arrowsize="1.0")

# 個体を表示
# query_bifd = g_bifd.query(
#     """SELECT ?uri ?name
#     WHERE {
#     ?uri rdf:type owl:NamedIndividual.
#     ?uri rdfs:label ?name.
#     }
#     """
# )
#
# for uri, name in query_bifd:
#     dg.node(str(uri), str(name))

dg.render(args.output)
