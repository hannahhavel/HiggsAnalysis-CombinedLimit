#!/usr/bin/env python3

import ROOT
import sys
import os
import json

def format_json(file_path, indent=4):
        try:
        with open(file_path, "r") as infile:
            data = json.load(infile)
        with open(file_path, "w") as outfile:
            json.dump(data, outfile, indent=indent, ensure_ascii=False)
        print(f"SUCCESS formatted JSON: {file_path}")
    except Exception as e:
        print(f"ERROR could not format JSON: {e}")

def export_workspace_to_json(input_root, output_json=None, ws_name="w"):
    #open ROOT file
    f = ROOT.TFile.Open(input_root, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"could not open ROOT file: {input_root}")

    #get workspace
    ws = f.Get(ws_name)
    if not ws:
        raise RuntimeError(f"workspace '{ws_name}' not found in file {input_root}")

    #define output file if not givne
    print(f"found workspace: {ws.GetName()}")
    if not output_json:
        base = os.path.splitext(os.path.basename(input_root))[0]
        output_json = f"{base}.json"

    #use RooJSONFactoryWSTool to export
    tool = ROOT.RooJSONFactoryWSTool(ws)
    tool.exportJSON(output_json)  #only argument is the filename

    #make JSON pretty
    format_json(output_json)

    print(f"exported workspace to JSON: {output_json}")

    f.Close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_ws.py <input.root> [output.json] [workspace_name]")
        sys.exit(1)

    input_root = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    ws_name = sys.argv[3] if len(sys.argv) > 3 else "w"

    export_workspace_to_json(input_root, output_json, ws_name)

