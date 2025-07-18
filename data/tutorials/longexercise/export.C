{
  auto f = TFile::Open("comb.root");
  auto* w = (RooWorkspace*) f->Get("w");
  RooFit::JSONIO::loadExportKeys("exportkeys.json");
  auto mytool = RooJSONFactoryWSTool(*w);
  mytool.exportJSON("comb.json");
}
