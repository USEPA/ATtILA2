# LandCoverClassificationEditor.pyw
# Michael A. Jackson
#
# Workaround for issue where User Account Control (UAC) dialog appeared behind geoprocessing window using os.startfile with .exe
# This script is in the middle since .pyw files do not cause the UAC fire alarms to go off.


import os
currentFolder = os.path.dirname(__file__)
exeName = 'LandCoverClassificationEditor.exe'
exePath = os.path.join(currentFolder, exeName)
os.startfile(exePath)

