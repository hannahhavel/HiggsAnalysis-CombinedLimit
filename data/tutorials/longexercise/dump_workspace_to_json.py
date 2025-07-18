#!/usr/bin/env python3

import ROOT
import sys
import os
import json  

def format(json_file_path, indent=4):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"JSON file '{json_file_path}' pretty printed with indent={indent}.")
    except Exception as e:
        print(f"warning: could not 'pretty print' JSON file '{json_file_path}': {e}")

#usage statement
def main():
    if len(sys.argv) != 2:
        print("usage: python dump_workspace_to_json.py <workspace.root>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + ".json"
    export_keys_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exportkeys.json")

    print(f"Input ROOT workspace file: {input_file}")
    print(f"Output JSON file will be: {output_file}")
    print(f"Export keys JSON file expected at: {export_keys_file}")

    #load Combine library
    #necessary for classes RooJSONFactoryWSTool and RooFit::JSONIO?
    if not ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so"):
        print("could not load")

    #open input .root file
    f = ROOT.TFile.Open(input_file)
    if not f or f.IsZombie():
        print(f"error: could not open file '{input_file}'.")
        sys.exit(1)

    ws = f.Get("w")
    if not ws or not ws.InheritsFrom("RooWorkspace"):
        print("error: could not find RooWorkspace 'w' in the input file.")
        sys.exit(1)

    print("successfully loaded RooWorkspace 'w' from file.")

    #load export keys
    try:
        loaded = ROOT.RooFit.JSONIO.loadExportKeys(export_keys_file)
    except Exception as e:
        print(f"exception raised while loading export keys: {e}")
        sys.exit(1)

    if not loaded:
        print(f"failed to load export keys from {export_keys_file}.")
        sys.exit(1)
    else:
        print("export keys loaded successfully.")

    #error testing for a specific type
    test_key = "SimpleGaussianConstraint"
    keys = ROOT.RooFit.JSONIO.exportKeys(test_key)
    if not keys:
        print(f"warning: No export keys found for '{test_key}'")
    else:
        print(f"export keys for '{test_key}': {keys}")

    #export workspace to JSON
    try:
        tool = ROOT.RooJSONFactoryWSTool(ws)
        success = tool.exportJSON(output_file)
    except Exception as e:
        print(f"exception raised during JSON export: {e}")
        sys.exit(1)

    if not success:
        print("error: exportJSON() export failed.")
        sys.exit(1)

    #pretty print JSON after export
    format(output_file)

    print(f"JSON successfully exported to: {output_file}")

if __name__ == "__main__":
    main()

