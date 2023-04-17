import os
import numpy as np
import rasterio
import geopandas as gpd
import rasterstats as rs
import pandas as pd
import errno

##Parameters
    ## file - A filename of the shapefile that the user want to extract the values for (string). The shapefile can be polygon, point, and polyline.
        ###Please note that for point shapefile, all the operations will result in same value
    ## raster_layers - A list of raster layers that the user want to extract values from (list of np array). For example, [ndvi, ndri, cvi]
    ## Affine_list - A list of affine values for each raster layer. Affine values should be in "affine.Affine" format. For example, affine values for "raster1"
    ## can be retrieved as raster1.profile["transform"]
    ## operations_list - A list of strings, each string corresponds to operations such as sum, mean, median, etc. For example, ["sum", "mean"]
    ## write - Pass "True" if the values are to be written to a csv file. If not, pass "False"
    ## outputfile - The filename of the csv file that user want to write the values into. The name should be <str>. The file gets saved into the current working directory

##Returns
    ## A pandas dataframe that contains the values as per user argument (nrows * ncols), where nrows represents number of shape features in shapefile and
    ## ncols represents number of raster layers * number of operations for each layer

def extract_values(file, raster_layers, Affine_list, operations_list, write=False, outputfile=None):

    #checking if the passed arguments are correct
    if isinstance(raster_layers, list) and isinstance(operations_list, list):
        shapefile = gpd.read_file (file)
        extracted_values=pd.DataFrame([])

    #iterating over indices layers provided by the user
        for raster, affine in zip(raster_layers, Affine_list):
            #performing the zonal statistics using rasterstats
            zonal_data = rs.zonal_stats(shapefile, raster, nodata=-999,
                                                   affine= affine,
                                                   geojson_out=True,
                                                   copy_properties=True,
                                                   stats=operations_list)


            #converting the zonal stats to geopandas dataframe
            zonal_data_df=gpd.GeoDataFrame.from_features(zonal_data)

            #extracting only the columns pertaining to the indices and operations
            operations= operations_list
            select=zonal_data_df[operations_list]

            #creating list for the name of indices and hence the name of the columns by appending operatin name to the index name
            rastername = [name for name in globals() if globals()[name] is raster]
            rasternames= [rastername[0] + "_" + operation for operation in operations ]

            #assigning column names to the dataframe
            select.columns=rasternames

            #appending the columns for each indices layer
            extracted_values = pd.concat([extracted_values, select], axis=1)

        ## if write argument is passed True, csv file is written and also dataframe is returned
        if write:
            extracted_values.to_csv(os.path.join(os.getcwd(), outputfile + ".csv"))
            return extracted_values

        ## if write argument is passed False, csv file is not written but dataframe is returned
        else:
            return extracted_values

    else:
        raise ValueError ("Either indices_layer or operations_list is not a list")

## extract_values("Plots.shp", [ndvi, ndri, cvi],[rast1, rast1, rast1], ["sum", "median", "mean"], write=False)
