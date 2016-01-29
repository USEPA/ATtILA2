'''
Test to evaluate consistency of LandCoverProportion Calculation

Created on Jul 3, 2012

@author: thultgren Torrin Hultgren, hultgren.torrin@epa.gov
'''

import arcpy
import ATtILA2
import filecmp
import parameters as p

def runTest():
    try:
        if arcpy.Exists(p.outTable):
            arcpy.Delete_management(p.outTable)
        ATtILA2.metric.runLandCoverProportions(p.inReportingUnitFeature, p.reportingUnitIdField, p.inLandCoverGrid, 
                                               p._lccName, p.lccFilePath, p.metricsToRun, p.outTable, p.processingCellSize, 
                                               p.snapRaster, p.optionalFieldGroups)
    
        result = filecmp.cmp(p.outTable, p.testLandCoverOutput, False)
        print result
    
    except Exception, e:
        ATtILA2.errors.standardErrorHandling(e)
        
if __name__ == '__main__':
    runTest()