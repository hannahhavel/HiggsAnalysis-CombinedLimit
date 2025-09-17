#!/usr/bin/env python3

import ROOT
import sys
import os
import json

def format_json(file_path, indent=4):
    """Pretty-print JSON with indentation."""
    try:
        with open(file_path, "r") as infile:
            data = json.load(infile)
        with open(file_path, "w") as outfile:
            json.dump(data, outfile, indent=indent, ensure_ascii=False)
        print(f"[OK] Formatted JSON: {file_path}")
    except Exception as e:
        print(f"[WARN] Could not format JSON: {e}")

def export_workspace_to_json(input_root, output_json=None, ws_name="w"):
    #open ROOT file
    f = ROOT.TFile.Open(input_root, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open ROOT file: {input_root}")

    #get workspace
    ws = f.Get(ws_name)
    if not ws:
        raise RuntimeError(f"Workspace '{ws_name}' not found in file {input_root}")

    print(f"[INFO] Found workspace: {ws.GetName()}")

    #define output name if not given
    if not output_json:
        base = os.path.splitext(os.path.basename(input_root))[0]
        output_json = f"{base}.json"

    #use RooJSONFactoryWSTool to export
    tool = ROOT.RooJSONFactoryWSTool(ws)
    tool.exportJSON(output_json)

    #make JSON pretty
    format_json(output_json)

    print(f"[DONE] Exported workspace to JSON: {output_json}")

    f.Close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_ws.py <input.root> [output.json] [workspace_name]")
        sys.exit(1)

    input_root = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    ws_name = sys.argv[3] if len(sys.argv) > 3 else "w"

    export_workspace_to_json(input_root, output_json, ws_name)

