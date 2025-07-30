import ROOT
import os
import sys

def test_json_import(json_file, workspace_name="w"):
    """test JSON import into RooWorkspace using RooJSONFactoryWSTool"""
    try:
        print(f"testing JSON import from: {json_file}")

        ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

        #create workspace and tool
        ws = ROOT.RooWorkspace(workspace_name)
        tool = ROOT.RooJSONFactoryWSTool(ws)

        #import JSON file
        tool.importJSON(json_file)

        #print workspace contents 
        ws.Print()


        #save workspace to a ROOT file
        #output_file = os.path.splitext(json_file)[0] + "_imported.root"
        #ws.writeToFile(output_file)
        #print(f"workspace saved to: {output_file}")

        return True

    except Exception as e:
        print(f"error: {str(e)}")
        return False

if __name__ == "__main__":
    test_json = "analysis_shapes_4.json"  #hardcoded (updated) JSON file to test
    if not os.path.exists(test_json):
        print(f"error: JSON file '{test_json}' not found")
        exit(1)

    if len(sys.argv) < 1:
        print("Usage: python test_model_tools.py <input.json>") #usage statement
        sys.exit(1)

    success = test_json_import(test_json)

    #0=success, 1=failure
    exit(0 if success else 1)
