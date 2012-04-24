""" Launch the Land Cover Classification (LCC) Editor
 
    Workaround for issue where User Account Control (UAC) dialog appeared behind geoprocessing window using os.startfile 
    with .exe.  

"""


import os
currentFolder = os.path.dirname(__file__)
exeName = 'LandCoverClassificationEditor.exe'
exePath = os.path.join(currentFolder, exeName)
os.startfile(exePath)

