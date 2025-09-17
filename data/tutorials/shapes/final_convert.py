import sys
import ROOT
import json

if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} input.root output.json")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

#open ROOT file and get workspace
f = ROOT.TFile.Open(input_file)
ws = f.Get("w")

#load custom export keys
ROOT.RooFit.JSONIO.loadExportKeys("exportkeys.json")

#export JSON (initially compact)
temp_json_file = "temp.json"
tool = ROOT.RooJSONFactoryWSTool(ws)
tool.exportJSON(temp_json_file)

#pretty-print JSON
with open(temp_json_file, "r") as f:
    data = json.load(f)

with open(output_file, "w") as f:
    json.dump(data, f, indent=2)

