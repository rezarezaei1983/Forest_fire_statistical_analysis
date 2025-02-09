"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                              <<< SOME NOTES >>>                               #
#                                                                               # 
#>>> This script calculates the paired t-test to show the statistical           #
#    significance of the difference between the pre-fire and post-fire NDVI.    #
#                                                                               #
#>>> The input files must be in GeoTIFF format.                                 #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@author : Reza Rezaei
email   : rezarezaei2008@gmail.com
version : 1.0
year    : 2024
"""

import os
import datetime
import numpy.ma as ma
import rasterio as rio
import scipy.stats as stats 
from contextlib import redirect_stdout


class PairedTTest:
    def __init__(self, reference_raster, last_raster, variable_name, area_name, 
                output_dir):    
        self.ref = reference_raster
        self.lst = last_raster
        self.var = variable_name
        self.area = area_name
        self.outdir = output_dir
        self.mask_val = -1000
        
    def GetRasterData(self, raster):
        file_name = os.path.basename(raster)
        date = file_name.split("_")[-2].split("T")[0]
        datetime_date = datetime.datetime.strptime(date, '%Y%m%d').strftime("%b %d %Y")

        with rio.open(raster) as src:
            arr_data = src.read(1)
            data_scale_factor = float(src.tags(bidx=0)["SCALE_FACTOR"])
            masked_arr_data = ma.masked_where(arr_data == self.mask_val, arr_data)
            masked_arr_data = masked_arr_data * data_scale_factor
            masked_arr_data = masked_arr_data.flatten()
        
        return masked_arr_data, datetime_date
    
    def PairedT_Test(self, pre_arr, post_arr, pre_date, post_date):
        stat, pvalue = stats.ttest_rel(pre_arr, post_arr) 
        pre_mean = pre_arr.mean()
        post_mean = post_arr.mean()
        
        if pvalue < 0.05:
            note = f"NOTE: There is statistically significant difference between "\
                   f"the {self.var} values of two groups."
        else:
            note = f"NOTE: There is NOT statistically significant difference between "\
                    "the {self.var} values of two groups."
        pvalue = f"{pvalue:.4f}"
          
        txt = ""
        txt += f"          ***      Test Summary     ***          \n\n"
        txt += f"Variable Name: {self.var}\n"
        txt += f"Study Area Name: {self.area}\n"  
        txt += f"Date of the Reference {self.var}: {pre_date}\n"
        txt += f"Date of the Last {self.var}     : {post_date}\n"
        txt += f"{'_' * 50}\n\n"
        txt += f"          *** Paired T-Test Results ***          \n\n"
        txt += f"P-value: {pvalue}\n"
        txt += f"T-value: {stat}\n\n"
        txt += f"Average {self.var} of the Reference Date: {pre_mean}\n"
        txt += f"Average {self.var} of the Last Date     : {post_mean}\n\n"
        txt += note
        
        var_name = self.var.replace(" ", "_")
        output_file = f"Paired-t-test_results_{self.var}-values_{self.area}.txt"
        output_path = os.path.join(self.outdir, output_file)
        with open(output_path, "w", encoding="utf-8") as file:
            with redirect_stdout(file):
                print(f"{txt}")
        
        return output_path
    
    def Run(self):
        pre_masked_arr, pre_datetime = self.GetRasterData(self.ref)
        post_masked_arr, post_datetime = self.GetRasterData(self.lst)
        
        non_masked_pre_elements = pre_masked_arr.count(axis = 0)
        non_masked_post_elements = post_masked_arr.count(axis = 0)
        
        pre_masked_arr = ma.array(pre_masked_arr, mask=ma.getmask(post_masked_arr))
        post_masked_arr = ma.array(post_masked_arr, mask=ma.getmask(pre_masked_arr))
        
        if pre_masked_arr.count(axis = 0) == post_masked_arr.count(axis = 0):
            pre_masked_arr = pre_masked_arr.compressed()            
            post_masked_arr = post_masked_arr.compressed()
            output_path = self.PairedT_Test(pre_arr=pre_masked_arr, 
                                            post_arr=post_masked_arr, 
                                            pre_date=pre_datetime, 
                                            post_date=post_datetime)
            print(f"\nThe outputs are written in:\n{output_path}")
        else:
            print("The length of data in two groups are not equal. So, the " \
                  "paired t-test is not applicable.")



#===================================== RUN ====================================

ref_rstr = "E:/My_articles/6- Wildfire/Data/Indicators_revised/Indicators/AD/NDVI/cropped_AD01_Pre-fire_NDVI_20210724T081609_20m.tif"
lst_rstr = "E:/My_articles/6- Wildfire/Data/Indicators_revised/Indicators/AD/NDVI/cropped_AD01_Post-fire_NDVI_20240728T081609_20m.tif"
var_name = "NDVI"
area_name = "Adana_01"
out_dir = "E:/My_articles/6- Wildfire/Data/Indicators_revised/"



ins = PairedTTest(reference_raster=ref_rstr, 
                  last_raster=lst_rstr, 
                  variable_name=var_name,
                  area_name=area_name,
                  output_dir=out_dir)
ins.Run()
