""" Open ATtILA Online Help
	
	Opens ATtILA's Github Wiki home page (https://github.com/USEPA/ATtILA2/wiki) in the 
	default web browser. If the web browser is already open, the home page will open in a 
	new window.
    
    No Arguments.
"""

import webbrowser
import arcpy

def main(_argv):
      
    helpURL = 'https://github.com/USEPA/ATtILA2/wiki' 
    startMsg = "\nThe full path to ATtILA's wiki home page:"
    indentMsg = "    "
    endMsg = "\n"+"You may close ArcGIS without disrupting the browser."+"\n"

    
    arcpy.AddMessage(startMsg)
    arcpy.AddMessage(indentMsg + helpURL)
    arcpy.AddMessage(endMsg)
    
    webbrowser.open(helpURL)

    
if __name__ == "__main__":
    main(sys.argv)