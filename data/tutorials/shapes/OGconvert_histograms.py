#!/usr/bin/env python3

import ROOT 
import json  
import sys
import os


def find_histograms(root_file):
    histograms = []

    def scan_directory(directory, path=""):
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            obj_path = f"{path}/{key.GetName()}" if path else key.GetName()

            if obj.InheritsFrom(ROOT.TH1.Class()):
                histograms.append((obj, obj_path))  
            elif obj.InheritsFrom(ROOT.TDirectory.Class()):
                scan_directory(obj, obj_path)

    scan_directory(root_file)
    return histograms


def convert_histograms_to_json(input_file, output_file=None):
    try:
        root_file = ROOT.TFile.Open(input_file)
        if not root_file or root_file.IsZombie():
            raise RuntimeError(f"could not open {input_file}")

        output_data = {
            "metadata": {
                "hs3_version": "0.2",
                "packages": [
                    {
                        "name": "ROOT",
                        "version": ROOT.gROOT.GetVersion().split('/')[0]
                    }
                ]
            },
            "data": []
        }

        histograms = find_histograms(root_file)

        for hist, path in histograms:
            output_data["data"].append({
                "name": path,  
                "type": "binned",
                "axes": [
                    {
                        "edges": [hist.GetXaxis().GetBinLowEdge(i) for i in range(0, hist.GetNbinsX() + 2)],
                        "name": "x"
                    }
                ],
                "contents": [hist.GetBinContent(i) for i in range(0, hist.GetNbinsX() + 2)],
                "errors": [hist.GetBinError(i) for i in range(0, hist.GetNbinsX() + 2)]
            })

        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_convert.json"

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"successfully exported {len(histograms)} histograms to {output_file}")
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


