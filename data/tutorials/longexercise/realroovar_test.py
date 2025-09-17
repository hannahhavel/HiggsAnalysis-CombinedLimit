import ROOT

f = ROOT.TFile.Open("datacard_part2.shapes.root")
ws = f.Get("w")  
ws.Print()       

vars = ws.allVars()
vars.Print("v")  

