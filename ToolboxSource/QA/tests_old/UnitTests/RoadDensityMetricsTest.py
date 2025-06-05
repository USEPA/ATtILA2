'''
Test to evaluate consistency of Road Density Metrics Calculation routine

Created Feburary 2013

@author: thultgren Torrin Hultgren, hultgren.torrin@epa.gov
'''

import arcpy
import ATtILA2
import parameters as p
import outputValidation

def runTest():
    try:
        if arcpy.Exists(p.outTable):
            arcpy.Delete_management(p.outTable)
            
        arcpy.AddMessage "Running Road Density calculation"
        ATtILA2.metric.runRoadDensityCalculator(p.rdinReportingUnitFeature, p.rdreportingUnitIdField, p.inRoadFeature, 
                                                p.outTable, p.roadClassField, p.streamsByRoads, p.roadsNearStreams, 
                                                p.inStreamFeatures, p.bufferDistance, p.rdoptionalFieldGroups)
    
        arcpy.AddMessage "Testing Road Density results"
        #results = outputValidation.compare(p.refLandCoverOutput,p.outTable)
        
        #arcpy.AddMessage results
    
    except Exception, e:
        ATtILA2.errors.standardErrorHandling(e)
        
if __name__ == '__main__':
    runTest()
