"""
Last Update 3/4/2025
@author: JTafrate

Use this code to process ATtILA Log files in .txt format to xml metadata. 
Currently this scrit works for the following tools
    - Land Cover Proportions (Working)
    - Land Cover on Slope Proportions (Working)
    - Neighborhood Proportions (Working)
    - Population in Floodplain (Working)
    - Road Density (Working)
    - Riparian Land Cover Proportions (Working)
    - Stream Density (Working)
    - Select Zonal Statistics (Working)

    (All other tools prcessing steps and table information is filled in. Use code 'NEEDED' to find items like idAbs which can be filled in manually) 

    *** Currently QA fields and AREA fields if selected will give a DESCRIPTION NEEDED 
"""


# Import Packages
import os
from lxml import etree
import arcpy
import xml.dom.minidom
import datetime
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.features import FeatureLayer
import pandas
from pandas.api.types import is_numeric_dtype
import re
from AttrDictISO import AttrDict # use the copy in each folder
from GlobalConstantsISO import *
import difflib

#Make this so it joins workspace and the outputfile name in thee export.
template = sys.argv[1]
path = sys.argv[2]
outWorkspace = sys.argv[3]
outFile = sys.argv[4]

def log_extract(file): # takes file path for .txt file, must be run first
    txt_file = open(file, "r")
    r_data = txt_file.readlines()
    def keyword_extract(keyword): # extract information into list from desired keywords
        empty_list = []
        for line in r_data: 
            if keyword in line:
                empty_list.append(line.strip())
        return empty_list
    specs = keyword_extract(BaseConstants.specs)  # probably all of this can be simplified and cleaned, but easy for now to change output
    tool = keyword_extract(BaseConstants.tool)
    params = keyword_extract(BaseConstants.params)
    FIELDS = keyword_extract(BaseConstants.FIELDS)
    fields =  keyword_extract(BaseConstants.fields)
    cell_size = keyword_extract(BaseConstants.cell_size)
    start_time = keyword_extract(BaseConstants.start_time)
    end_time = keyword_extract(BaseConstants.end_time)
    proc_steps = keyword_extract(BaseConstants.proc_steps)
    bounds = keyword_extract(BaseConstants.bounds)
    metrics = keyword_extract(BaseConstants.metrics)
    neighborhood = keyword_extract(BaseConstants.neighborhood)
    slope_thresh = keyword_extract(BaseConstants.slope_thresh)
    buff = keyword_extract(BaseConstants.buff)
    outTable = keyword_extract(BaseConstants.outTable)
    statsType = keyword_extract(BaseConstants.statsType)
    
    proc_steps = [item for item in proc_steps if not any(keyword in item for keyword in ["[CMD]","CLASS"])]
    return specs, tool, params, FIELDS, fields, cell_size, start_time, end_time, proc_steps, bounds, metrics, neighborhood, slope_thresh, buff, outTable, statsType
#output different lists based off the keywords written in the function, these can be changed as needed

specs, tool, params, FIELDS, fields, cell_size, start_time, end_time, proc_steps, bounds, metrics, neighborhood, slope_thresh, buff, outTable, statsType = log_extract(path)

def XML_metadata():
    #1. retrive constants class from the tool name
    shortName = tool[0].split(';')[1].strip(' ')
    constantStr = shortName + "Constants"

    if constantStr in globals(): 
        constant = globals()[constantStr]
    else: 
        constant = Unknown
    def update_themes(): 
        for theme in root.findall('.//themeKeys'): # Find all themekeys
            title = theme.find('thesaName').find('resTitle')
        
        if title.text == 'User': # Only update the user defined keywords
            for key in constant.themekey_list: 
                themekey = etree.SubElement(theme, 'keyword')
                themekey.text = key  
        
    def update_place():
        for placeKeys in root.findall('.//placeKeys'): # iterate into the place element
            for keyword in placeKeys.findall('keyword'): # find all placekeys to remove
                placeKeys.remove(keyword)

            for key in BaseConstants.placekey_list:
                keyword = etree.SubElement(placeKeys, 'keyword')
                keyword.text = key 
    
    def update_distinfo(): 
        distTranOps = root.find('distInfo').find('distTranOps')
        for item in BaseConstants.links: #this may need to be built out into a dictionary
            onlineSrc = etree.SubElement(distTranOps, 'onlineSrc')
            onlineSrc.attrib['xmlns'] = ''
            linkage = etree.SubElement(onlineSrc, 'linkage')
            linkage.text = item
            protocol = etree.SubElement(onlineSrc, 'protocol')
            protocol.text = 'NEEDED'
            orFunct = etree.SubElement(onlineSrc, 'orFunct')
            onFunctCd = etree.SubElement(orFunct, 'onFunctCd')
            onFunctCd.attrib['value'] = 'NEEDED'

    def update_idinfo():
        title = root.find('dataIdInfo').find('idCitation').find('resTitle') 
        title.text = constant.title

        eadetcit = root.find('eainfo').find('overview').find('eadetcit')
        eadetcit.text = BaseConstants.newlink

        eaover = root.find('eainfo').find('overview').find('eaover')
        eaover.text = ('These layers describe land cover characteristics derived using the '
                '{0} tool from the ATtILA toolbox for ArcGIS Pro (v2.8). '
                'https://www.epa.gov/enviroatlas/attila-toolbox. ' 
                'A list of creation steps is included in the Processing Steps.'.format(shortName))

        abstract = root.find('dataIdInfo').find('idAbs')
        if constant == SZSConstants: # include the stats list in the abstract for zonal statistics
            statsList = statsType[0].split('=')[1].strip().replace(';',',') 
            abstract.text = (constant.abstract).format(statsList=statsList) 
        else:
            abstract.text = (constant.abstract)
        
        purpose = root.find('dataIdInfo').find('idPurp')
        purpose.text = (constant.purpose)

        linkage = root.find('Esri').find('DataProperties').find('itemProps').find('itemLocation').find('linkage')
        linkage.text = path[path.find(r"\Profile"):]

        itemName = root.find('Esri').find('DataProperties').find('itemProps').find('itemName')
        itemName.text = path.split("\\")[-1].split("_2")[0]

        envirDesc = root.find('dataIdInfo').find('envirDesc')
        envirDesc.text = specs[0].replace("SPECS: ", "")
    
    def add_procstep(): #this function is complex and maybe not so clear. It does work though
        procdates = []
        procdescs = [] 
        for item in proc_steps: # split the info from the earlier log file into date and description 
            date, step = item.split(']',1)
            procdates.append(date.strip('[]'))
            procdescs.append(step) 

        dataLineage = root.find('dqInfo').find('dataLineage')
        
        for date, desc in zip (procdates,procdescs): 
            prcStep = etree.SubElement(dataLineage, 'prcStep')
            prcStep.attrib['xmlns'] = ''

            stepDesc = etree.SubElement(prcStep, 'stepDesc')
            stepDesc.text = desc

            stepDateTm = etree.SubElement(prcStep, 'stepDateTm')
            stepDateTm.text = date 

    def add_attributes(): #There is some repetition here ad it could be made a bit cleaner
        detailed = root.find('eainfo').find('detailed')
        detailed.attrib['Name'] = tool[0].split(':')[1].split(';')[0].strip()
        enttypl = detailed.find('enttyp').find('enttypl')
        enttypl.text = tool[0].split(':')[1].split(';')[0].strip()
        enttypt = detailed.find('enttyp').find('enttypt')
        if constant != NPConstants: 
            enttypt.text = 'Table'
        else: 
            enttypt.text = 'NEEDED'
        enttypc = detailed.find('enttyp').find('enttypc')
        # add the text here once the logfiles are updated to include the count of rows.

        enttypd = detailed.find('enttyp').find('enttypd')
        enttypd.text = 'ATtILA Processing Record' # Ask Jeremy/Don what to put here


        if constant == NPConstants: # This one operated differently since attribte info is not in the logfile
            info, num = neighborhood[0].split('=')
            num = num.strip(" ")

            outputs = re.findall(r'\[(.*?)\]',metrics[0])

            detailed = root.find('eainfo').find('detailed')
            for item in outputs:
                attr = etree.Element('attr')
                attr.attrib['xmlns'] = ''
                attrlabl = etree.SubElement(attr, 'attrlabl')
                attrlabl.attrib['Sync'] = 'TRUE'
                attrlabl.text = item
                attalias = etree.SubElement(attr, 'attalias')
                attalias.text = item
                attrtype = etree.SubElement(attr, 'attrtype')
                attrtype.attrib['Sync'] = 'TRUE'
                attrtype.text = 'INSERT DATA TYPE'
                attwidth = etree.SubElement(attr, 'attwidth') #Aks Jeremy/Don about this
                attwidth.attrib['Sync'] = 'TRUE'
                attwidth.text = 'NEEDED'
                atprecis = etree.SubElement(attr, 'atprecis') #Ask Jeremy/Don about this
                atprecis.attrib['Sync'] = 'TRUE'
                atprecis.text = 'NEEDED'
                attscale = etree.SubElement(attr, 'attscale') #Ask Jeremy/Don about this
                attscale.attrib['Sync'] = 'TRUE'
                attscale.text = 'NEEDED'

                attrdef = etree.SubElement(attr, 'attrdef')
                if item in AttrDict.keys(): 
                    attrdef.text = AttrDict[item].format(num=num) 
                else:
                    attrdef.text = 'DESCRIPTION NEEDED'
                    
                attrdefs = etree.SubElement(attr, 'attrdefs')
                attrdefs.text = 'US EPA'
                    
                attrdomv = etree.SubElement(attr, 'attrdomv')
                rdom = etree.SubElement(attrdomv, 'rdom') 
                rdom.attrib['xmlns'] = ''
                rdommin = etree.SubElement(rdom, 'rdommin')
                rdommin.text = '0%'
                rdommax = etree.SubElement(rdom, 'rdommax')
                rdommax.text = '100%'
            
                detailed.append(attr)
            return None 
        
        elif constant == LCOSPConstants: 
            for item in slope_thresh: 
                info, slope_dist = item.split('=', 1)
                slope = slope_dist.strip('" ').rstrip(',')

            detailed = root.find('eainfo').find('detailed')
            for item in FIELDS:

                fieldName = item.split(':')[1].split(';')[1].strip()
                fieldType = item.split(':')[1].split(';')[2].strip()
                fieldWidth = item.split(':')[1].split(';')[3].strip()
                fieldPrecis = item.split(':')[1].split(';')[4].strip()
                fieldScale =  item.split(':')[1].split(';')[5].strip()
                fieldMin = item.split(':')[1].split(';')[6].strip()
                fieldMax = item.split(':')[1].split(';')[7].strip()
            
                lookup_name = re.sub('\d', '', fieldName)
               
                if fieldType not in ['OID', 'FID', 'ID']:
                    attr = etree.Element('attr')
                    attr.attrib['xmlns'] = ''
                    attrlabl = etree.SubElement(attr, 'attrlabl')
                    attrlabl.attrib['Sync'] = 'TRUE'
                    attrlabl.text = fieldName
                    attalias = etree.SubElement(attr, 'attalias')
                    attalias.attrib['Sync'] = 'TRUE'
                    attalias.text = fieldName

                    attrtype = etree.SubElement(attr, 'attrtype')
                    attrtype.attrib['Sync'] = 'TRUE'
                    attrtype.text = fieldType

                    attwidth = etree.SubElement(attr, 'attwidth') #WARNING, I am assuming length and width to be interchangable here
                    attwidth.attrib['Sync'] = 'TRUE'
                    attwidth.text = fieldWidth
                    
                    atprecis = etree.SubElement(attr, 'atprecis') 
                    atprecis.attrib['Sync'] = 'TRUE'
                    atprecis.text = fieldPrecis

                    attscale = etree.SubElement(attr, 'attscale') #Ask Jeremy/Don about this
                    attscale.attrib['Sync'] = 'TRUE'
                    attscale.text = fieldScale

                    #update attrdef info
                    attrdef = etree.SubElement(attr, 'attrdef')
                    if fieldName in AttrDict.keys(): 
                        attrdef.text = AttrDict[fieldName]
                    elif lookup_name in AttrDict.keys(): 
                        attrdef.text = AttrDict[lookup_name].format(slope=slope)
                    else:
                        attrdef.text = 'DESCRIPTION NEEDED'
                    #update attrdefs
                    attrdefs = etree.SubElement(attr, 'attrdefs')
                    if fieldName == 'HUC_12': 
                        attrdefs.text = BaseConstants.HUC_12_defs
                    else:
                        attrdefs.text = 'US EPA'
                    
                    attrdomv = etree.SubElement(attr, 'attrdomv')
                    if fieldMin != "NA":
                        rdom = etree.SubElement(attrdomv, 'rdom') 
                        rdom.attrib['xmlns'] = ''
                        rdommin = etree.SubElement(rdom, 'rdommin')
                        rdommin.text = fieldMin
                        rdommax = etree.SubElement(rdom, 'rdommax')
                        rdommax.text = fieldMax
                            
                    else:
                        codesetd = etree.SubElement(attrdomv, 'codesetd')
                        codesets = etree.SubElement(codesetd, 'codesets')
                        codesets.text = 'NEEDED'
                
                    detailed.append(attr)
            return None     
        
        elif constant == RLCPConstants:
            for item in buff[:1]: 
                info, buff_dist = item.split('=', 1)
            dist = buff_dist.strip('" ').rstrip('s').strip()

            detailed = root.find('eainfo').find('detailed')

            for item in FIELDS:

                fieldName = item.split(':')[1].split(';')[1].strip()
                fieldType = item.split(':')[1].split(';')[2].strip()
                fieldWidth = item.split(':')[1].split(';')[3].strip()
                fieldPrecis = item.split(':')[1].split(';')[4].strip()
                fieldScale =  item.split(':')[1].split(';')[5].strip()
                fieldMin = item.split(':')[1].split(';')[6].strip()
                fieldMax = item.split(':')[1].split(';')[7].strip()

                if fieldType not in ['OID', 'FID', 'ID']:
                    attr = etree.Element('attr')
                    attr.attrib['xmlns'] = ''
                    attrlabl = etree.SubElement(attr, 'attrlabl')
                    attrlabl.attrib['Sync'] = 'TRUE'
                    attrlabl.text = fieldName
                    attalias = etree.SubElement(attr, 'attalias')
                    attalias.attrib['Sync'] = 'TRUE'
                    attalias.text = fieldName

                    attrtype = etree.SubElement(attr, 'attrtype')
                    attrtype.attrib['Sync'] = 'TRUE'
                    attrtype.text = fieldType

                    attwidth = etree.SubElement(attr, 'attwidth') #WARNING, I am assuming length and width to be interchangable here
                    attwidth.attrib['Sync'] = 'TRUE'
                    attwidth.text = fieldWidth
                    
                    atprecis = etree.SubElement(attr, 'atprecis') 
                    atprecis.attrib['Sync'] = 'TRUE'
                    atprecis.text = fieldPrecis

                    attscale = etree.SubElement(attr, 'attscale') #Ask Jeremy/Don about this
                    attscale.attrib['Sync'] = 'TRUE'
                    attscale.text = fieldScale

                    attrdef = etree.SubElement(attr, 'attrdef')
                    lookup_name = re.sub('\d', '', fieldName)
                   # Update attrname and attrdef
                    if fieldName in AttrDict.keys(): 
                        attrdef.text = AttrDict[fieldName]
                    elif lookup_name in AttrDict.keys(): 
                        attrdef.text = AttrDict[lookup_name].format(dist=dist)
                    else:
                        attrdef.text = 'DESCRIPTION NEEDED'
                    #update attrdefs
                    attrdefs = etree.SubElement(attr, 'attrdefs')
                    if fieldName == 'HUC_12': 
                        attrdefs.text = BaseConstants.HUC_12_defs
                    else:
                        attrdefs.text = 'US EPA'

                    attrdomv = etree.SubElement(attr, 'attrdomv')
                    if fieldMin != "NA":
                        rdom = etree.SubElement(attrdomv, 'rdom') 
                        rdom.attrib['xmlns'] = ''
                        rdommin = etree.SubElement(rdom, 'rdommin')
                        rdommin.text = fieldMin
                        rdommax = etree.SubElement(rdom, 'rdommax')
                        rdommax.text = fieldMax
                            
                    else:
                        codesetd = etree.SubElement(attrdomv, 'codesetd')
                        codesets = etree.SubElement(codesetd, 'codesets')
                        codesets.text = 'NEEDED'
                
                    detailed.append(attr)
            return None                     
        
        elif constant == SZSConstants:
            detailed = root.find('eainfo').find('detailed')

            for item in FIELDS:
            
                fieldName = item.split(':')[1].split(';')[1].strip()
                fieldType = item.split(':')[1].split(';')[2].strip()
                fieldWidth = item.split(':')[1].split(';')[3].strip()
                fieldPrecis = item.split(':')[1].split(';')[4].strip()
                fieldScale =  item.split(':')[1].split(';')[5].strip()
                fieldMin = item.split(':')[1].split(';')[6].strip()
                fieldMax = item.split(':')[1].split(';')[7].strip()
                if fieldType not in ['OID', 'FID', 'ID']:
                    attr = etree.Element('attr')
                    attr.attrib['xmlns'] = ''
                    attrlabl = etree.SubElement(attr, 'attrlabl')
                    attrlabl.attrib['Sync'] = 'TRUE'
                    attrlabl.text = fieldName
                    attalias = etree.SubElement(attr, 'attalias')
                    attalias.attrib['Sync'] = 'TRUE'
                    attalias.text = fieldName

                    attrtype = etree.SubElement(attr, 'attrtype')
                    attrtype.attrib['Sync'] = 'TRUE'
                    attrtype.text = fieldType

                    attwidth = etree.SubElement(attr, 'attwidth') #WARNING, I am assuming length and width to be interchangable here
                    attwidth.attrib['Sync'] = 'TRUE'
                    attwidth.text = fieldWidth
                    
                    atprecis = etree.SubElement(attr, 'atprecis') 
                    atprecis.attrib['Sync'] = 'TRUE'
                    atprecis.text = fieldPrecis

                    attscale = etree.SubElement(attr, 'attscale') #Ask Jeremy/Don about this
                    attscale.attrib['Sync'] = 'TRUE'
                    attscale.text = fieldScale

                    attrdef = etree.SubElement(attr, 'attrdef')
                    
                    #here think about how to strip out the statistic information, perhaps using some kind of list matching
                    lastMatch = None 
                    for key in AttrDict: 
                        if key in fieldName: 
                            lastMatch = key 
                    if lastMatch: 
                        attrdef.text = AttrDict[lastMatch]
                    else:  
                        attrdef.text = 'DESCRIPTION NEEDED'

                    attrdefs = etree.SubElement(attr, 'attrdefs')
                    if fieldName == 'HUC_12': 
                        attrdefs.text = BaseConstants.HUC_12_defs
                    else:
                        attrdefs.text = 'US EPA'
                        
                    attrdomv = etree.SubElement(attr, 'attrdomv')
                        # currently sets min and max under attrdomv SubElement for each one with numbers
                    if fieldMin != "NA":
                        rdom = etree.SubElement(attrdomv, 'rdom') 
                        rdom.attrib['xmlns'] = ''
                        rdommin = etree.SubElement(rdom, 'rdommin')
                        rdommin.text = fieldMin
                        rdommax = etree.SubElement(rdom, 'rdommax')
                        rdommax.text = fieldMax
                            
                    else:
                        codesetd = etree.SubElement(attrdomv, 'codesetd')
                        codesets = etree.SubElement(codesetd, 'codesets')
                        codesets.text = 'NEEDED'
                
                    detailed.append(attr)
            return None 
        
        else: 
            detailed = root.find('eainfo').find('detailed')
            for item in FIELDS:
            
                fieldName = item.split(':')[1].split(';')[1].strip()
                fieldType = item.split(':')[1].split(';')[2].strip()
                fieldWidth = item.split(':')[1].split(';')[3].strip()
                fieldPrecis = item.split(':')[1].split(';')[4].strip()
                fieldScale =  item.split(':')[1].split(';')[5].strip()
                fieldMin = item.split(':')[1].split(';')[6].strip()
                fieldMax = item.split(':')[1].split(';')[7].strip()

                if fieldType not in ['OID', 'FID', 'ID']:
                    attr = etree.Element('attr')
                    attr.attrib['xmlns'] = ''
                    attrlabl = etree.SubElement(attr, 'attrlabl')
                    attrlabl.attrib['Sync'] = 'TRUE'
                    attrlabl.text = fieldName
                    attalias = etree.SubElement(attr, 'attalias')
                    attalias.attrib['Sync'] = 'TRUE'
                    attalias.text = fieldName

                    attrtype = etree.SubElement(attr, 'attrtype')
                    attrtype.attrib['Sync'] = 'TRUE'
                    attrtype.text = fieldType

                    attwidth = etree.SubElement(attr, 'attwidth') #WARNING, I am assuming length and width to be interchangable here
                    attwidth.attrib['Sync'] = 'TRUE'
                    attwidth.text = fieldWidth
                    
                    atprecis = etree.SubElement(attr, 'atprecis') 
                    atprecis.attrib['Sync'] = 'TRUE'
                    atprecis.text = fieldPrecis

                    attscale = etree.SubElement(attr, 'attscale') #Ask Jeremy/Don about this
                    attscale.attrib['Sync'] = 'TRUE'
                    attscale.text = fieldScale

                    attrdef = etree.SubElement(attr, 'attrdef')
                    if fieldName in AttrDict.keys(): 
                        attrdef.text = AttrDict[fieldName] 
                    else:
                        attrdef.text = 'DESCRIPTION NEEDED'
                    
                    attrdefs = etree.SubElement(attr, 'attrdefs')
                    if fieldName == 'HUC_12': 
                        attrdefs.text = BaseConstants.HUC_12_defs
                    else:
                        attrdefs.text = 'US EPA'
                        
                    attrdomv = etree.SubElement(attr, 'attrdomv')
                    if fieldMin != "NA":
                        rdom = etree.SubElement(attrdomv, 'rdom') 
                        rdom.attrib['xmlns'] = ''
                        rdommin = etree.SubElement(rdom, 'rdommin')
                        rdommin.text = fieldMin
                        rdommax = etree.SubElement(rdom, 'rdommax')
                        rdommax.text = fieldMax
                            
                    else:
                        codesetd = etree.SubElement(attrdomv, 'codesetd')
                        codesets = etree.SubElement(codesetd, 'codesets')
                        codesets.text = 'MISSING'
                
                    detailed.append(attr)
            return None 
    
    def add_bounds(): 
        for item in bounds: 
            info, coords = item.split('=', 1)
        coord_list = [coord.strip() for coord in coords.split(',')]
        west = root.findall('.//westBL')
        west[0].text = coord_list[2]

        east = root.findall('.//eastBL')
        east[0].text = coord_list[0]

        north = root.findall('.//northBL')
        north[0].text = coord_list[1]

        south = root.findall('.//southBL')
        south[0].text = coord_list[3]
       # return None
    
    def update_dates(): #Change this to all the right paths
        today = datetime.datetime.now()
        
        # Publication Dates
        pubDate = root.find('dataIdInfo').find('idCitation').find('date').find('pubDate')
        pubDate.text = '{0}'.format(today.strftime('%Y%m%d'))

        mdDateSt = root.find('mdDateSt')
        mdDateSt.text = '{0}'.format(today.strftime('%Y%m%d'))

        today_plus_5 = today.replace(year=today.year+5)
        dateNext = root.find('mdMaint').find('dateNext')
        dateNext.text = '{0}'.format(today_plus_5.strftime('%Y%m%d'))

        # Processing Start and end
        tmBegin = root.findall('.//tmBegin')
        tmBegin[0].text = start_time[0]
        tmEnd = root.findall('.//tmEnd')
        tmEnd[0].text = end_time[0]

    update_themes() 
    update_place() 
    update_idinfo() 
    add_procstep() 
    add_attributes() 
    add_bounds() 
    update_dates() 
    update_distinfo()
    
 
parser = etree.XMLParser(remove_blank_text=True)
root = etree.parse(template, parser=parser).getroot() #define the root before running the function

XML_metadata() # This is the main function call

xmlstr = xml.dom.minidom.parseString(etree.tostring(root)).toprettyxml()
print(xmlstr)
#print('Done')

def saveXML(xmlstring):
    save_path_file = os.path.join(str(outWorkspace),str(outFile))
    arcpy.AddMessage(f"XML metadata saved to {save_path_file}")
 
    with open(save_path_file, "w") as f: 
        f.write(xmlstring) 

saveXML(xmlstr)