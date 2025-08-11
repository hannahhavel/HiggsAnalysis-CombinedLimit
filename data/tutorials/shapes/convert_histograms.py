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
            #0 to N+2 to extract 'underflow' and 'overflow' bins
            edges = [hist.GetXaxis().GetBinLowEdge(i) for i in range(0, hist.GetNbinsX() + 2)]
            contents = [hist.GetBinContent(i) for i in range(0, hist.GetNbinsX() + 2)]
            errors = [hist.GetBinError(i) for i in range(0, hist.GetNbinsX() + 2)]

            for i in range(len(contents)):
                output_data["data"].append({
                    "name": name,
                    "type": "binned",
                    "axes": [
                        {
                            "edges": edges,
                            "name": "x"
                        }
                    ],
                    "bin": i,  #bin index
                    "content": contents[i],
                    "error": errors[i]
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


