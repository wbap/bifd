# bif_excel2owl.py
Python script to convert a BIF file in the Excel format to the OWL format.

USE: python bif_excel2owl.py config bifd_path infile outfile  
(Download the bifd.owl from [here](https://raw.githubusercontent.com/wbap/bifd/master/bifd.owl).)  
(For config example, see old.json.)  
(Now it uses rdflib instead of owlready2.)

As for a BIF Excel format, see [this document](https://docs.google.com/document/d/1kKGJeG_NjuWqp7uUYvcb_uBiahj7KS_rKfhxtS4LP3c/edit?usp=sharing).

TODO: properties: transmitter, implementation, modType, Taxon, and Size
