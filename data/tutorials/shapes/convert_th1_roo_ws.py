#!/usr/bin/env python3

import ROOT
import json
import sys
import os

ROOT.RooFit.JSONIO.importExpressions()

#make JSON pretty
def format_json(file_path, indent=4):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        print(f"successfully formatted: {file_path}")
    except Exception as e:
        print(f"error formatting: {e}")

#wrap all histograms into a workspace (recursively)
def wrap_histograms_in_workspace(root_file):
    ws = ROOT.RooWorkspace("w")
    histogram_count = 0

    def scan_directory(directory):
        nonlocal histogram_count
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.TH1.Class()):
                histogram_count += 1
                #one RooRealVar per histogram axis
                #the tool expects this
                xaxis = obj.GetXaxis()
                xvar = ROOT.RooRealVar(
                    f"x_{obj.GetName()}",
                    f"x_{obj.GetName()}",
                    xaxis.GetXmin(),
                    xaxis.GetXmax()
                )
                dh = ROOT.RooDataHist(obj.GetName(), obj.GetTitle(),
                                      ROOT.RooArgList(xvar), obj)
                getattr(ws, "import")(dh)
            elif obj.InheritsFrom(ROOT.TDirectory.Class()):
                scan_directory(obj)

    scan_directory(root_file)
    print(f"converted {histogram_count} histograms into workspace.")
    return ws

#convert everything in ROOT file to HS3 JSON
def convert_to_json(input_file, output_file=None):
    root_file = ROOT.TFile.Open(input_file)
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"could not open {input_file}")

    if not output_file:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.json"

    #if workspaces exist in file, export them directly
    keys = root_file.GetListOfKeys()
    exported = False
    for key in keys:
        obj = key.ReadObj()
        if obj.InheritsFrom(ROOT.RooWorkspace.Class()):
            ws_name = obj.GetName()
            print(f"found workspace '{ws_name}' → exporting")
            tool = ROOT.RooJSONFactoryWSTool(obj)
            tool.exportJSON(output_file)
            exported = True

    #if no workspace, build one from histograms
    if not exported:
        print("no RooWorkspace found → wrapping histograms instead")
        ws = wrap_histograms_in_workspace(root_file)
        tool = ROOT.RooJSONFactoryWSTool(ws)
        tool.exportJSON(output_file)

    format_json(output_file)
    print(f"exported file: {output_file}")

    root_file.Close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python convert_all_noskim.py <input.root> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert_to_json(input_file, output_file)

