import arcpy
import pandas as pd
from pandas import DataFrame

def fc_to_pd_df(feature_class, field_list):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param feature_class: Input ArcGIS Feature Class.
    :param field_list: Fields for input.
    :return: Pandas DataFrame object.
    """
    return DataFrame(
        arcpy.da.FeatureClassToNumPyArray(
            in_table=feature_class,
            field_names=field_list,
            skip_nulls=False,
            null_value=-99999
        )
    )

def table_to_pd_df(table): 
    """Similar to the above function, this turns a table in a gdb to Pandas
    Data Frame for subsequent analysis
    """
    data = []
    fields = [f.name for f in arcpy.ListFields(table)]
    with arcpy.da.SearchCursor(table,fields) as cursor: 
        for row in cursor:
            data.append(row)
    df = pd.DataFrame(data,columns=fields)
    return df