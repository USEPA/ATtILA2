# LandCoverClassificationEditor.pyw
# Michael A. Jackson
#
# Workaround for issue where User Account Control (UAC) dialog appeared behind geoprocessing window using os.startfile with .exe
# This script is in the middle since .pyw files do not cause the UAC fire alarms to go off.


import os
import sys

os.startfile(os.path.basename(sys.argv[0]).replace(".pyw", ".exe"))

