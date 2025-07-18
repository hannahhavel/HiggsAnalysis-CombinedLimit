#!/usr/bin/env python3

import ROOT
import sys
import os

# Fail fast if wrong usage
if len(sys.argv) != 2:
    print("Usage: python dump_workspace_to_json.py <input_root_workspace>")
    sys.exit(1)

# Load Combine library (adjust path if needed!)
ROOT.gSystem.Load("../../build/libHiggsAnalysisCombinedLimit.so")

# Input and output paths
input_file = sys.argv[1]
if not os.path.isfile(input_file):
    print(f"Error: file '{input_file}' does not exist")
    sys.exit(1)

output_file = os.path.splitext(input_file)[0] + ".json"

# Load workspace
f = ROOT.TFile.Open(input_file)
ws = f.Get("w")

if not ws or not ws.InheritsFrom("RooWorkspace"):
    print("Error: Could not find RooWorkspace 'w' in the input file.")
    sys.exit(1)

# Dump to JSON
json_tool = ROOT.RooFactoryJSONTOOL(ws)
success = json_tool.exportJSON(output_file)

if not success:
    print("Error: Failed to export workspace to JSON.")
    sys.exit(1)

print(f"Successfully wrote: {output_file}")

