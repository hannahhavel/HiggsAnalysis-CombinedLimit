#!/usr/bin/env python3

import ROOT #ROOT library
import json #JSON file operations
import sys
import os

#convert TH1 histograms to JSON
def convert_histograms_to_json(input_file, output_file=None): 
    try:
        root_file = ROOT.TFile.Open(input_file)
        if not root_file or root_file.IsZombie():
            raise RuntimeError(f"could not open {input_file}")

        #access histograms
        directory = root_file.Get("signal_region") #directory where histograms exist 
        if not directory:
            raise RuntimeError("directory 'signal_region' not found")

        #HS3 metadata (printed at top of .json)
        output_data = {
            "metadata": {
                "hs3_version": "0.2",
                "packages": [  #added to avoid metadata error
                    {
                        "name": "ROOT",
                        "version": ROOT.gROOT.GetVersion().split('/')[0]  
                    }
                ]
            },
            "data": []  
        }

        #process histograms
        for key in directory.GetListOfKeys():
            name = key.GetName()
            hist = directory.Get(name)

            #if not a histogram or TH1 histogram
            if not hist or not hist.InheritsFrom(ROOT.TH1.Class()):
                continue

            #format for data in histograms
            #HS3-compatible JSON format
            output_data["data"].append({
                "name": name,
                "type": "binned",
                "axes": [
                    {
                        "edges": [hist.GetXaxis().GetBinLowEdge(i) for i in range(0, hist.GetNbinsX()+2)],
                        "name": "x"
                    }
                ],
                #0 to N+2 to extract 'underflow' and 'overflow' bins
                "contents": [hist.GetBinContent(i) for i in range(0, hist.GetNbinsX()+2)],
                "errors": [hist.GetBinError(i) for i in range(0, hist.GetNbinsX()+2)]
            })

        #set output filename (if not given provided)
        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_convert.json"

        #write to output
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"successfully exported to {output_file}")
        return output_data

    except Exception as e:
        print(f"error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'root_file' in locals():
            root_file.Close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python convert_histograms.py <input.root> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_histograms_to_json(input_file, output_file)

