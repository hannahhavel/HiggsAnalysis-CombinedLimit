import ROOT
import os
import sys

def test_json_import(json_file):
    """test JSON import into RooWorkspace using RooJSONFactoryWSTool"""
    try:
        print(f"testing JSON import from: {json_file}")

        #load libraries
        ROOT.gSystem.Load("libRooFit")
        ROOT.gSystem.Load("libRooFitHS3")

        #not used:
        #ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

        #create workspace and tool
        ws = ROOT.RooWorkspace("w")
        tool = ROOT.RooJSONFactoryWSTool(ws)

        #import JSON file
        print("attempting import...")
        if not tool.importJSON(json_file):
            raise RuntimeError("import failed w/o error message")

        #print contents
        print("\nworkspace contents:")
        ws.Print()

        #checking imported histograms from .json
        hist_names = [key.GetName() for key in ws.allData()]
        if not hist_names:
            raise RuntimeError("no histograms found in workspace")

        print(f"\nsuccessfully imported {len(hist_names)} histograms")
        return True

    except Exception as e:
        print(f"\nerror: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python test_model_toolsv2.py <input.json>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"error: file '{json_file}' not found")
        sys.exit(1)

    success = test_json_import(json_file)
    sys.exit(0 if success else 1)

