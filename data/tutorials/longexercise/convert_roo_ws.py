#!/usr/bin/env python3

import ROOT
import json
import sys
import os

#make JSON pretty
def format_json(file_path, indent=2):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"successfully formatted: {file_path}")
    except Exception as e:
        print(f"error formatting: {e}")

#if workspaces exist in file, export full ws directly
def convert_workspace_to_json(input_file, output_file=None, ws_name="w"):
    root_file = ROOT.TFile.Open(input_file)
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"could not open {input_file}")

    #get an existing RooWorkspace
    ws = root_file.Get(ws_name)
    if not ws or not ws.InheritsFrom(ROOT.RooWorkspace.Class()):
        raise RuntimeError(f"workspace '{ws_name}' not found in {input_file}")

    print(f"found workspace '{ws_name}'")

    if not output_file:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.json"

    #export JSON using HS3 tool
    tool = ROOT.RooJSONFactoryWSTool(ws)
    temp_file = "temp_export.json"
    tool.exportJSON(temp_file)
    format_json(temp_file)
    
    #rename temp file to final output
    os.rename(temp_file, output_file)
    print(f"exported workspace to {output_file}")

    root_file.Close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python convert_workspace_full.py <input.root> [output.json] [workspace_name]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    ws_name = sys.argv[3] if len(sys.argv) > 3 else "w"

    convert_workspace_to_json(input_file, output_file, ws_name)
