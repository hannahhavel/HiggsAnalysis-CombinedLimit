#!/usr/bin/env python3
import ROOT
import os

#minimal reproducer to test if: JSON structure is valid HS3 and can be imported
def load_hs3_json(json_path):
    #check file exists
    try:
        open(json_path).close()
    except FileNotFoundError:
        print(f"file not found: {json_path}")
        raise

    #create workspace
    ws = ROOT.RooWorkspace("w")
    tool = ROOT.RooJSONFactoryWSTool(ws)

    print(f"loading HS3 JSON file: {json_path}")

    #import JSON into workspace
    tool.importJSON(json_path)
    return ws



#usage statement
if len(os.sys.argv) != 2:
    print(f"usage: {os.path.basename(__file__)} <.json file>")
    os.sys.exit(1)

json_file = os.sys.argv[1]

#attempt to load the JSON file
ws = load_hs3_json(json_file)

#confirm if it was loaded successfully
print(f"workspace '{ws.GetName()}' loaded successfully.")
