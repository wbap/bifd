# bifsmw2owl
- To convert a BIFD Semantic MediaWiki dump (rdf) to the OWL format
- including:
  - converter.py: the main OWL conversion code
  - The following scripts create input files for converter.py
    - restriction_mapping.py: to extract constraints in bifd.owl to a JSON file
    - mapping.py: to create class mapping
    - mapping_predicate.py: to create predicate mapping

## What is required
- Install rdflib (4.2.2 verified)
- Input files
  - dump.rdf (Semantic MediaWiki dump)
  - header.rdf (prefixes [RDF/XML])
  - bifd.owl (BIF ontology file)

## Running the converter
```
# -m is an option for not deleting working files
./bifsmw2owl.sh -b (BIF ontology file) -d (semantic mediawiki dump) -h (header.rdf) -o (output file) -m
```
- Output file
  - converted.owl
- Working files
  - s.tsv (subject, object URI mapping)
  - p.tsv (predicate URI mapping)
