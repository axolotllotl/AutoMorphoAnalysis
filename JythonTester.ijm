output = File.getParent(getInfo("macro.filepath")) + "/results/"


// runs the python script

jythonText = File.openAsString(File.getParent(getInfo("macro.filepath")) + "/ColocalizationDataCompiler.py"); 
call("ij.plugin.Macro_Runner.runPython", jythonText, output); 

waitForUser("Finished!", "Analysis Complete!");
