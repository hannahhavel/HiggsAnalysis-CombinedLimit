

        #!/usr/bin/env python

import ROOT
import json
import sys
import os

#print JSON with formatting
def format_json(file_path, indent=4):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        print(f"successfully formatted: {file_path}")
    except Exception as e:
        print(f"error formatting: {e}")

#wrap TH1 histograms into a RooWorkspace (recursively from all directories)
def wrap_histograms_in_workspace(root_file):
    ws = ROOT.RooWorkspace("w")
    histogram_count = 0  #counter for summary

    #get information from histograms
    def scan_directory(directory):
        nonlocal histogram_count
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.TH1.Class()):
                histogram_count += 1
                xvar = ROOT.RooRealVar("x", "x",
                                       obj.GetXaxis().GetXmin(),
                                       obj.GetXaxis().GetXmax())
                dh = ROOT.RooDataHist(obj.GetName(), obj.GetTitle(),
                                      ROOT.RooArgList(xvar), obj)
                getattr(ws, "import")(dh)
            elif obj.InheritsFrom(ROOT.TDirectory.Class()):
                scan_directory(obj)

    scan_directory(root_file)
    print(f"converted {histogram_count} histograms.")
    return ws

#convert file to HS3 JSON
def convert_workspace_to_json(input_file, output_file=None):
    root_file = ROOT.TFile.Open(input_file)
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"could not open {input_file}")


   #CHANGED: try to get an existing RooWorkspace named "w"
    ws = root_file.Get("w")
    if ws and isinstance(ws, ROOT.RooWorkspace):
        print("Found existing RooWorkspace 'w' in file, using it.")
    else:
        print("No RooWorkspace 'w' found in file, wrapping TH1 histograms into a new workspace.")


    ws = wrap_histograms_in_workspace(root_file)

    if not output_file:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.json"

    #export JSON using HS3 tool
    tool = ROOT.RooJSONFactoryWSTool(ws) #used in prototype
    tool.exportJSON(output_file)

    format_json(output_file)

    print(f"exported file: {output_file}")

    root_file.Close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        #usage statement
        print("usage: python convert_histograms.py <input.root> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_workspace_to_json(input_file, output_file)


