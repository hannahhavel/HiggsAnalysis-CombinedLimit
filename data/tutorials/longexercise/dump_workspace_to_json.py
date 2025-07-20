#!/usr/bin/env python3

import ROOT #ROOT library for histogram handling
import json #JSON file operations
import sys 
import os
import re


#extract bin contents (values) and errors for a ROOT histogram (TH1)
def extract_hist_data(hist):
    return {
        #0 to N+2 to extract 'underflow' and 'overflow' bins
        "values": [hist.GetBinContent(i) for i in range(0, hist.GetNbinsX()+2)],
        "errors": [hist.GetBinError(i) for i in range(0, hist.GetNbinsX()+2)]
    }

#store histogram in standard dictionary format
def store_histogram(container, name, hist):
    container[name] = {
        "name": hist.GetName(),
        "type": hist.ClassName(),
        "axes": [{ #all axis metadata
            "name": hist.GetXaxis().GetName(),
            "nbins": hist.GetNbinsX(),
            "min": hist.GetXaxis().GetXmin(),
            "max": hist.GetXaxis().GetXmax()
        }],
        #0 to N+2 to store 'underflow' and 'overflow' bins
        "values": [hist.GetBinContent(i) for i in range(0, hist.GetNbinsX()+2)],
        "errors": [hist.GetBinError(i) for i in range(0, hist.GetNbinsX()+2)],
        "integral": hist.Integral(), #total integral (sum of bin contents)
        "systematics": {}  #empty to start
    }

#link systematic variations to their nominal histograms
#'up' and 'down' variations (histogram pairs)
def process_systematics(systematics_map, output_data):
    for base_name, variations in systematics_map.items():
        #handle both formats: process_CMS_sys and process_sys
        #parse systematic name (CMS and non-CMS formats)
        parts = base_name.split("_CMS_") if "_CMS_" in base_name else base_name.rsplit("_", 1)
        process = parts[0]
        sys_name = "CMS_" + parts[1] if "_CMS_" in base_name else parts[1] if len(parts) > 1 else "unknown"

        #if nominal histogram is missing: create placeholder
        if process not in output_data["histograms"]:
            print(f"Note: Found systematics for '{base_name}' but no nominal histogram, still including")
            output_data["histograms"][process] = {
                "name": process,
                "type": "TH1D", #default type, may differ later
                "axes": [],
                "values": [],
                "errors": [],
                "integral": 0,
                "systematics": {}
            }

        #add all systematic variations ('up' and 'down') if they exist
        if "Up" in variations or "Down" in variations:
            if "systematics" not in output_data["histograms"][process]:
                output_data["histograms"][process]["systematics"] = {}

            if "Up" in variations: #+1σ variation
                output_data["histograms"][process]["systematics"][sys_name] = {
                    "Up": extract_hist_data(variations["Up"])
                }
            if "Down" in variations: #-1σ variation
                if sys_name not in output_data["histograms"][process]["systematics"]:
                    output_data["histograms"][process]["systematics"][sys_name] = {}
                output_data["histograms"][process]["systematics"][sys_name]["Down"] = extract_hist_data(variations["Down"])

#main histogram extraction function to convert ROOT histograms to JSON format
def extract_histograms_to_json(input_file, output_file=None):
    try:
        #input file (ROOT)
        root_file = ROOT.TFile.Open(input_file)
        if not root_file or root_file.IsZombie():
            raise RuntimeError(f"Could not open {input_file}")

        #output structure (schema)
        output_data = {
            "histograms": {},
            "metadata": {
                "source_file": os.path.basename(input_file),
                "format": "hs3",
                "analysis_type": "shape"
            }
        }

        #access histograms directory
        dir_name = "signal_region" #may differ later
        directory = root_file.Get(dir_name)
        if not directory:
            raise RuntimeError(f"Directory '{dir_name}' not found")

        #scan histograms
        systematics_map = {} 
        total_histograms = 0 #TH1-derived objects
        nominal_count = 0 #non-systematic histograms
        systematic_count = 0 #'up' and 'down' variations

        #count all histograms
        for key in directory.GetListOfKeys():
            name = key.GetName()
            obj = directory.Get(name)
            if obj and obj.InheritsFrom(ROOT.TH1.Class()):
                total_histograms += 1

        #process all histograms
        for key in directory.GetListOfKeys():
            name = key.GetName()
            obj = directory.Get(name)

            if not obj or not obj.InheritsFrom(ROOT.TH1.Class()):
                continue

            #classify systematic variations or nominal
            if name.endswith("Up") or name.endswith("Down"):
                base_name = name[:-2]
                direction = name[-2:]
                systematics_map.setdefault(base_name, {})[direction] = obj
                systematic_count += 1
            else:
                #store nominal (regular) histograms
                store_histogram(output_data["histograms"], name, obj)
                nominal_count += 1

        #link systematics
        process_systematics(systematics_map, output_data)

        #set output filename and write output (JSON)
        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_histograms.json"

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        #print summary
        #tot_systematics = sum(len(h["systematics"]) for h in output_data["histograms"].values())
        print(f"\nComplete:")
        print(f"Total TH1 objects found: {total_histograms}") #comparable to original .root 
        print(f"Nominal histograms: {nominal_count}")
        print(f"Systematic variations: {systematic_count}")
        print(f"Output saved to: {output_file}")

        return output_data

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'root_file' in locals():
            root_file.Close() #close file handle

#usage statement
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dump_histograms.py <input.root> [output.json]")
        sys.exit(1)

    extract_histograms_to_json(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

