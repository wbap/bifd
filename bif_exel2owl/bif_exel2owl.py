# -*- coding: utf-8 -*-
"""BIF_Exel2OWL.py
    USE: python bif_exel2owl.py infile bifd_url [outdir]
         outfile name is infile name + .owl
"""
import openpyxl
from owlready2 import *
import inspect

def createCircuits(ws):
    for p in range(2):
        for i in range(ws.max_row-1):
            val = ws.cell(row=i+2, column=1).value
            if val!=None and val.strip()!="":
                label = ws.cell(row=i+2, column=2).value
                parts = ws.cell(row=i+2, column=3).value
                pos = val.find(':')
                className = val.strip().replace(' ', '_') if pos<0 else val[pos+1:].strip().replace(' ', '_')
                if p==0:
                    clm4 = ws.cell(row=i+2, column=4).value	# Functionality
                    clm5 = ws.cell(row=i+2, column=5).value	# References
                    clm6 = ws.cell(row=i+2, column=6).value	# TODO: implementation
                    clm7 = ws.cell(row=i+2, column=7).value	# Uniform?
                    uniform = False
                    if clm7!=None and clm7:
                        uniform = True
                    with onto:
                        if uniform:
                            cls = types.new_class(className, (bifdns.UniformCircuit,))
                        else:
                            cls = types.new_class(className, (bifdns.Circuit,))
                        cls.label = label
                        if clm4!=None and clm4!="":
                            cls.functionality = clm4
                        if clm5!=None and clm5!="":
                            references = clm5.split(";")
                            cls.reference = references
                else:
                    addHasPart(parts, className)

def addHasPart(parts, className):
    if parts!=None:
        prts = parts.split(";")
        for part in prts:
            prt = None
            cls = None
            try:
                prt = eval("onto." + part.strip())
                cls = eval("onto." + className)
            except:
                continue
            if inspect.isclass(prt):
                # print(cls, cls.is_a)
                # print(bifdns.hasPart.some(prt))
                cls.is_a.append(bifdns.hasPart.some(prt))

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
            cls.label = label
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
    try:
        inputClass = eval("onto." + inputCircuit)
    except:
        print("No input circuit defined: " + inputCircuit)
        return
    try:
        outputClass = eval("onto." + outputCircuit)
    except:
        print("No output circuit defined: " + outputCircuit)
        return
    cls.is_a.append(bifdns.inputCircuit.some(inputClass))
    cls.is_a.append(bifdns.outputCircuit.some(outputClass))

if __name__=='__main__':
    if len(sys.argv)<=2:
        print("USE: python bif_exel2owl.py infile bifd_url [outdir]")
        print("     outfile name is infile name + .owl")
        exit()
    # wb=openpyxl.load_workbook('BG.DHBA.bif.xlsx')
    # bifd = get_ontology('https://raw.githubusercontent.com/wbap/bifd/master/bifd.owl').load()
    # onto = get_ontology("https://wba-initiative.org/bifd/BG_DHBA.owl")
    infilePath = sys.argv[1]
    if len(sys.argv)<=3:
        outfilePath = "./"
    else:
        outfilePath = sys.argv[3]
    lastSlash = infilePath.rfind('/')
    if lastSlash>=0:
        infileName = infilePath[lastSlash+1:]
    else:
        infileName = infilePath
    lastPoint = infileName.rfind('.')
    if lastPoint>=0:
        outfileName = infileName[0:lastPoint] + ".owl"
    else:
        outfileName = infileName + ".owl"

    wb=openpyxl.load_workbook(sys.argv[1])
    bifd = get_ontology(sys.argv[2]).load()
    onto = get_ontology("https://wba-initiative.org/bifd/" + outfileName)

    bifdns = bifd.get_namespace('https://wba-initiative.org/bifd/')
    # Defining annotation properties
    with bifdns:
        class functionality(comment):
            pass
        class reference(comment):
            pass
        class implementation(comment):
            pass

    createCircuits(wb['Circuit'])
    createConnections(wb['Connection'])
    onto_path.append(outfilePath)
    onto.save()
