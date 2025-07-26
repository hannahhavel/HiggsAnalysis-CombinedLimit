import ROOT
import os

def test_json_import(json_file, workspace_name, param_name):
    """tests the JSON workspace import functionality that will be used in ModelTools.py. 
       they handle: JSON file loading, workspace creation, JSON-to-workspace conversion, and parameter extraction"""
    try:
        print(f"testing JSON import from: {json_file}")

        # with open(fin, 'r') as json_file:
        #     wstmp = ROOT.RooWorkspace()
        #     jsontool = ROOT.RooFactoryJSONTOOL(wstmp)
        #     self.out.safe_import(wstmp.arg(rp), *importargs)

        with open(json_file, 'r') as f:
            #create temporary workspace (like wstmp)
            wstmp = ROOT.RooWorkspace("tmp_workspace")  
            
            #initialize JSON tool 
            jsontool = ROOT.RooFactoryJSONTOOL(wstmp)   
            
            #load JSON into workspace 
            jsontool.importJSON(json_file)              

            #validating if import worked
            param = wstmp.arg(param_name)
            if param:
                print(f"found '{param_name}' in JSON workspace")
                print(f"value = {param.getVal()}")
                return True
            else:
                print(f"failed: '{param_name}' not found in workspace")
                return False

    except Exception as e:
        print(f"error: {str(e)}")
        return False
    

if __name__ == "__main__":
    #initialize ROOT environment
    ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")  #needed for RooWorkspace

    #test configuration 
    test_json = "analysis_shapes_4.json" #JSON file to test
    test_ws   = "w"                      #workspace name in JSON
    test_param = "test_param"            #parameter to extract (like 'rp')

    if not os.path.exists(test_json):
        print(f"error: JSON file '{test_json}' not found")
        exit(1)

    success = test_json_import(test_json, test_ws, test_param)
    
    #exit code (0=success, 1=failure)
    exit(0 if success else 1)
