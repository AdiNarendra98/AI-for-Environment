#CHM height module. Given a x,y location and a pool of CHM images, find the matching location and extract the crown level CHM measurement
import glob
import numpy as np 
from src import neon_paths
import rasterstats
import geopandas as gpd
import pandas as pd

def non_zero_99_quantile(x):
    """Get height quantile of all cells that are no zero"""
    mdata = np.ma.masked_where(x < 0.5, x)
    mdata = np.ma.filled(mdata, np.nan)
    percentile = np.nanpercentile(mdata, 99)
    return (percentile)

def postprocess_CHM(df, lookup_pool):
    """Field measured height must be within min_diff meters of canopy model"""
    #Extract zonal stats, add a small offset, the min box can go to next tile.
    try:
        CHM_path = neon_paths.find_sensor_path(lookup_pool=lookup_pool, bounds=df.total_bounds)
    except Exception as e:
        raise ValueError("Cannot find CHM path for {} from plot {} in lookup_pool: {}".format(df.total_bounds, df.plotID.unique(),e))
    
    #buffer slightly, CHM model can be patchy
    geom = df.geometry
    draped_boxes = rasterstats.zonal_stats(geom,
                                           CHM_path,
                                           add_stats={'q99': non_zero_99_quantile})
    df["CHM_height"] = [x["q99"] for x in draped_boxes]

    #if height is null, try to assign it
    try:
        df.height.fillna(df["CHM_height"], inplace=True)
    except:
        print("No height column detected")  
    
    return df
        
def CHM_height(shp, CHM_pool):
        """For each plotID extract the heights from LiDAR derived CHM
        Args:
            shp: shapefile of data to filter
            config: DeepTreeAttention config file dict, parsed, see config.yml
        """    
        filtered_results = []
        lookup_pool = glob.glob(CHM_pool, recursive=True)        
        for name, group in shp.groupby("plotID"):
            try:
                result = postprocess_CHM(group, lookup_pool=lookup_pool)
                filtered_results.append(result)
            except Exception as e:
                print("plotID {} raised: {}".format(name,e))
                
        filtered_shp = gpd.GeoDataFrame(pd.concat(filtered_results,ignore_index=True))
        
        return filtered_shp

def height_rules(df, min_CHM_height=1, max_CHM_diff=4, CHM_height_limit=8):
    """Which data points should be included based on a comparison of CHM and field heights
        This is asymmetric, field heights under CHM height are signs of subcanopy, whereas CHM under field height is mismeasurement and growth. 
        Do not filter NA heights
    Args:
        df: a pandas dataframe with CHM_height and height columns
        min_CHM_height: if CHM is avialble, remove saplings under X meters
        max_CHM_diff: max allowed difference between CHM and field height if CHM > field height
        CHM_height_limit: max allowed difference between CHM and field height if CHM < field height
    Returns:
       df: filtered dataframe
    """
    keep = []
    for index, row in df.iterrows():
        if np.isnan(row["CHM_height"]):
            keep.append(False)
        elif np.isnan(row["height"]):
            keep.append(True)
        elif row.CHM_height < min_CHM_height:
            keep.append(False)
        elif row.CHM_height > row.height:
            if (row.CHM_height - row.height) >= max_CHM_diff:
                keep.append(False)
            else:
                keep.append(True)
        elif row.CHM_height <= row.height:
            if (row.height - row.CHM_height) >= CHM_height_limit:
                keep.append(False)
            else:
                keep.append(True)
        else:
            print("No conditions applied to CHM_height {}, height {}".format(row.CHM_height,row.height))
            keep.append(True)
            
    df["keep"] = keep
    df = df[df.keep]
    
    return df

def filter_CHM(shp, CHM_pool, min_CHM_height=1, max_CHM_diff=4, CHM_height_limit=8):
    """Filter points by height rules"""
    if min_CHM_height is None:
        return shp
    
    #extract CHM height
    shp = CHM_height(shp, CHM_pool)
    shp = height_rules(df=shp, min_CHM_height=1, max_CHM_diff=4, CHM_height_limit=8)

    return shp