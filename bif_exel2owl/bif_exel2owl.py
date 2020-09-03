# -*- coding: utf-8 -*-
"""BIF_Exel2OWL.py
    USE: python bif_exel2owl.py infile bifd_url outfile
"""
import openpyxl
from owlready2 import *
import inspect

def createCircuits(ws):
    for p in range(2):
        for i in range(ws.max_row-1):
            val = ws.cell(row=i+2, column=1).value
            if val!=None and val.strip()!="":
                labels = ws.cell(row=i+2, column=2).value
                parts = ws.cell(row=i+2, column=4).value
                superClasses = ws.cell(row=i+2, column=3).value
                pos = val.find(':')
                className = val.strip().replace(' ', '_') if pos<0 else val[pos+1:].strip().replace(' ', '_')
                if p==0:
                    clm4 = ws.cell(row=i+2, column=5).value	# Functionality
                    clm5 = ws.cell(row=i+2, column=6).value	# References
                    clm6 = ws.cell(row=i+2, column=7).value	# TODO: implementation
                    clm7 = ws.cell(row=i+2, column=8).value	# Uniform?
                    uniform = False
                    if clm7!=None and clm7:
                        uniform = True
                    with onto:
                        if uniform:
                            cls = types.new_class(className, (bifdns.UniformCircuit,))
                        else:
                            cls = types.new_class(className, (bifdns.Circuit,))
                        addLabels(labels, cls)
                        if clm4!=None and clm4!="":
                            cls.functionality = clm4
                        if clm5!=None and clm5!="":
                            references = clm5.split(";")
                            cls.reference = references
                else:
                    cls = eval("onto." + className)
                    addHasPart(parts, cls)
                    addSubClassOf(superClasses, cls)

def addLabels(labels, cls):
    if labels:
        lbls = labels.split(";")
        for label in lbls:
            cls.label.append(label)

def addHasPart(parts, cls):
    if parts:
        prts = parts.split(";")
        for part in prts:
            prt = eval("onto." + part.strip())
            if prt!= None and inspect.isclass(prt):
                # print(cls, cls.is_a)
                # print(bifdns.hasPart.some(prt))
                cls.is_a.append(bifdns.hasPart.some(prt))

def addSubClassOf(superClasses, cls):
    if superClasses:
        sups = superClasses.split(";")
        for superClassName in sups:
            sc = eval("onto." + superClassName.strip())
            if sc!= None and inspect.isclass(sc):
                cls.is_a.append(sc)

def createConnections(ws):
    for i in range(ws.max_row-1):
        inputCircuit = ""
        col1 = ws.cell(row=i+2, column=1).value
        if col1!=None and col1.strip()!="":
            pos = col1.find(':')
            inputCircuit = col1.strip().replace(' ', '_') if pos<0 else col1[pos+1:].strip().replace(' ', '_')
        outputCircuit = ""
        col2 = ws.cell(row=i+2, column=2).value
        if col2!=None and col2.strip()!="":
            pos = col2.find(':')
            outputCircuit = col2.strip().replace(' ', '_') if pos<0 else col2[pos+1:].strip().replace(' ', '_')
        if inputCircuit == "" or outputCircuit == "":
            continue
        connectionID = inputCircuit + "-" + outputCircuit
        with onto:
            cls = types.new_class(connectionID, (bifdns.Connection,))
            cls.label = connectionID
            addInOut(cls, inputCircuit, outputCircuit)
            clm3 = ws.cell(row=i+2, column=4).value	# TODO: Transmitter
            clm4 = ws.cell(row=i+2, column=4).value	# Functionality
            clm5 = ws.cell(row=i+2, column=5).value	# References
            if clm4!=None and clm4!="":
                cls.functionality = clm4
            if clm5!=None and clm5!="":
                references = clm5.split(";")
                cls.reference = references

def addInOut(cls, inputCircuit, outputCircuit):
    inputClass = eval("onto." + inputCircuit)
    if inputClass == None or not inspect.isclass(inputClass):
        print("No input circuit defined: " + inputCircuit)
        return
    outputClass = eval("onto." + outputCircuit)
    if outputClass == None or not inspect.isclass(outputClass):
        print("No output circuit defined: " + outputCircuit)
        return
    cls.is_a.append(bifdns.inputCircuit.some(inputClass))
    cls.is_a.append(bifdns.outputCircuit.some(outputClass))

if __name__=='__main__':
    if len(sys.argv)<=3:
        print("USE: python bif_exel2owl.py infile bifd_url outfile")
        exit()

    infilePath = sys.argv[1]
    outfilePath = sys.argv[3]
    lastSlash = infilePath.rfind('/')
    if lastSlash>=0:
        infileName = infilePath[lastSlash+1:]
    else:
        infileName = infilePath

    wb=openpyxl.load_workbook(sys.argv[1])
    bifd = get_ontology(sys.argv[2]).load()

    bifdns = bifd.get_namespace('https://wba-initiative.org/bifd/')
    # Defining annotation properties
    with bifdns:
        class functionality(comment):
            pass
        class reference(comment):
            pass
        class implementation(comment):
            pass

    # Defining an ontoloby
    project = wb['Project']
    pname = project.cell(row=2, column=1).value
    if not pname:
       print("Error: no project name")
       exit()
    description = project.cell(row=2, column=3).value
    onto = get_ontology("https://wba-initiative.org/wbra/" + pname +"/")
    onto.metadata.comment.append(description)

    createCircuits(wb['Circuit'])
    createConnections(wb['Connection'])
    # onto_path.append(outfilePath)
    onto.save(file=outfilePath)
