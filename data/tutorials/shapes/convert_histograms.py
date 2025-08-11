#convert_histograms.py
#!/usr/bin/env python

import ROOT #ROOT library
import json #JSON file operations
import sys
import os

#find all TH1 histograms (recursively) in the ROOT file
def find_histograms(root_file):
    histograms = []
    #in all directories
    def scan_directory(directory):
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.TH1.Class()):
                histograms.append(obj)
            elif obj.InheritsFrom(ROOT.TDirectory.Class()):
                scan_directory(obj)
    scan_directory(root_file)
    return histograms

#convert TH1 histograms to JSON
def convert_histograms_to_json(input_file, output_file=None):
    try:
        root_file = ROOT.TFile.Open(input_file)
        if not root_file or root_file.IsZombie():
            raise RuntimeError(f"could not open {input_file}")

        #find all histograms
        histograms = find_histograms(root_file)
        if not histograms:
            raise RuntimeError("no TH1 histograms found in file")

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

        #process histograms (restructured "data" entry so it is a list of flat dictionaries (per DataFrameWrapper.py))
        for hist in histograms:
            name = hist.GetName()
            nbins = hist.GetNbinsX()
            for i in range(0, nbins + 2):  #0 to N+2 to extract 'underflow' and 'overflow' bins
                low_edge = hist.GetXaxis().GetBinLowEdge(i)
                high_edge = hist.GetXaxis().GetBinUpEdge(i)
                content = hist.GetBinContent(i)
                error = hist.GetBinError(i)

                output_data["data"].append({
                    "name": name,
                    "type": "binned",
                    "axis_name": "x",
                    "axis_low_edge": low_edge,
                    "axis_high_edge": high_edge,
                    "bin": i,
                    "content": content,
                    "error": error,
                    "sum_w": content,
                    "sum_ww": error**2
                })

        #set output filename (if not given)
        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_converted.json"

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


