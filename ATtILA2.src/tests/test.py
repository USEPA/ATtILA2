'''
Created on Nov 1, 2011

@author: cerick02
'''
import esdlepy
import arcpy
outFilePath = r"c:\temp\outTest.txt"
esdlepy.arcpyh.reportToolResultsToFile(arcpy, outFilePath)