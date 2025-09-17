import ROOT
import sys

filename = sys.argv[1]
f = ROOT.TFile.Open(filename)

def scan_workspace(ws, path=""):
    print(f"{path}: RooWorkspace")
    # list all datasets (RooDataHist, RooDataSet)
    for d in ws.allData():
        print(f"{path}/{d.GetName()}: {d.ClassName()}")
    # list all PDFs
    for p in ws.allPdfs():
        print(f"{path}/{p.GetName()}: {p.ClassName()}")
    # list all variables
    for v in ws.allVars():
        print(f"{path}/{v.GetName()}: {v.ClassName()}")

def scan_directory(directory, path=""):
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        full_path = f"{path}/{key.GetName()}" if path else key.GetName()
        print(f"{full_path}: {obj.ClassName()}")

        if obj.InheritsFrom(ROOT.TDirectory.Class()):
            scan_directory(obj, full_path)
        elif obj.InheritsFrom(ROOT.RooWorkspace.Class()):
            scan_workspace(obj, full_path)

scan_directory(f)

