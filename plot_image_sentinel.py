#!/usr/bin/env python
# coding: utf-8

import argparse
from glob import glob
from datetime import datetime

import toml
import satpy
from satpy import demo
from satpy.scene import Scene
from satpy import find_files_and_readers
from pyresample.geometry import AreaDefinition
from satpy.resample import get_area_def

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import copy

from pathlib import Path
from satpy.utils import debug_on; debug_on()
import traceback


config = toml.load('config.toml')

parser = argparse.ArgumentParser(
                    prog = 'plot_overpass',
                    description = '',
                    epilog = '')

parser.add_argument('date', help='date to download %Y%m%d')
#parser.add_argument('--area', help='', default='ATKA')
#parser.add_argument('--replot', help='', default=False, action='store_true')

args = parser.parse_args()

satpy.config.set(config_path=['satpy_config'])

areadefs = {}
description = "ATKA in SouthPolarSt -15"
proj_dict = {"proj": "stere", "lat_0": -90, "lon_0": -15}
width = 14000 
width = 7000 
height = width*0.7342
# Area extent as a tuple (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
area_extent = (187000, 2120000,  330000, 2225000)
areadefs['ATKA'] = AreaDefinition("ATKA", "SouthPolarSt_-15", description, proj_dict, width, height, area_extent)
print(f'ATKA width, height for 300m  {(area_extent[2]-area_extent[0])/300:.2f}, {(area_extent[3]-area_extent[1])/300:.2f}')
print(f'ATKA current res [m]  {(area_extent[2]-area_extent[0])/width:.2f}, {(area_extent[3]-area_extent[1])/height:.2f}')

description = "ATKA2 in SouthPolarSt -15"
proj_dict = {"proj": "stere", "lat_0": -90, "lon_0": -15}
width = 8300 
height = width*0.6024
# Area extent as a tuple (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
area_extent = (240000, 2150000, 323000, 2200000)
areadefs['ATKA2'] = AreaDefinition("ATKA2", "SouthPolarSt_-15", description, proj_dict, width, height, area_extent)
print(f'ATKA2 current res [m]  {(area_extent[2]-area_extent[0])/width:.2f}, {(area_extent[3]-area_extent[1])/height:.2f}')

description = "CAPSarea in SouthPolarSt -15"
proj_dict = {"proj": "stere", "lat_0": -90, "lon_0": -15}
width = 9500 
height = width*0.73684
# Area extent as a tuple (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
area_extent =(85000, 2135000, 180000, 2205000)
areadefs['CAPSarea'] = AreaDefinition("CAPSarea", "SouthPolarSt_-15", description, proj_dict, width, height, area_extent)
print(f'CAPSarea current res [m]  {(area_extent[2]-area_extent[0])/width:.2f}, {(area_extent[3]-area_extent[1])/height:.2f}')

description = "ATKAstd in SouthPolarSt"
# PROJ.4 : +proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
proj_dict = {"proj": "stere", "lat_0": -90, 'lat_ts': -71, "lon_0": 0}
width = 5000 
height = width*1
# Area extent as a tuple (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
area_extent =(85000, 2135000, 180000, 2205000)
#Upper Left  ( -315239.500, 2143800.300) (  8d21'54.81"W, 70d14'49.58"S)
#Lower Left  ( -315239.500, 2093800.300) (  8d33'43.42"W, 70d41'22.87"S)
#Upper Right ( -265239.500, 2143800.300) (  7d 3'10.87"W, 70d18'25.56"S)
#Lower Right ( -265239.500, 2093800.300) (  7d13'10.88"W, 70d45' 4.19"S)
#Center      ( -290239.500, 2118800.300) (  7d48' 0.00"W, 70d30' 0.00"S)
area_extent = (-315239.5, 2093800.2999999998, -265239.5, 2143800.3)
areadefs['ATKAstd'] = AreaDefinition("ATKAstd", "SouthPolarSt", description, proj_dict, width, height, area_extent)
print(f'ATKAstd current res [m]  {(area_extent[2]-area_extent[0])/width:.2f}, {(area_extent[3]-area_extent[1])/height:.2f}')

#areadef = areadefs["CAPSarea"]
areadef = areadefs["ATKA2"]
areadef = areadefs["ATKAstd"]

# https://github.com/PolarGeospatialCenter/comnap-antarctic-facilities/blob/master/dist/csv/COMNAP_Antarctic_Facilities_Master.csv

poi_list = [
    ((-8.266667, -70.666667), 'NIII'),
    ((-2.840324, -71.672873), 'SANAE'),
    ((2.53307, -72.011946), 'TROLL'),
    ((11.832151, -70.775796), 'NOVO'),
    ((-25.473889, -75.571111), 'HALLEY'),
    ((23.346891, -71.949858), 'PE'),
    ((8.833333, -71.533333), 'WFR'),
    ((0.066667, -75.000000), 'KOH'), 
]

f_coast_o = '/mnt/c/Users/Radenz/localdata/bas_antarctic_coastlines/medium_res_line_v7_5/add_coastline_medium_res_line_v7_5_reproj.shp'
f_coast_o = '/home/traceairmass/sat_imagergy/bas_antarctic_coastlines/medium_res_line_v7_5/add_coastline_medium_res_line_v7_5_reproj.shp'
f_coast_o = '/sat_imag/bas_antarctic_coastlines/medium_res_line_v7_5/add_coastline_medium_res_line_v7_5_reproj.shp'

composites = {
     'false_color': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     'true_color': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     'natural_color': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     #'false_color_hr': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     #'day_microphysics_hr': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     #'snow_hires': {'polycolor': 'grey', 'gridcolor': 'lightgrey'},
     #'snow_age': {'polycolor': 'grey', 'gridcolor': 'lightgrey'},
     #'microphysics24': {'polycolor': 'grey', 'gridcolor': 'lightgrey'},
     'true_color_sharp': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     'natural_color_sharp': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
     'natural_color_enh': {'polycolor': 'brown', 'gridcolor': 'lightgrey'},
 }


coast_citation = "Gerrish et al. 2022. Medium resolution vector polylines of the Antarctic coastline https://doi.org/10.5285/4e09c5d9-edf4-448e-aea7-2e56e9376aae"

def plot_scene(scene, sat, rgb_type, areadef, outpath, pc):
    scene.load([rgb_type])
    new_scn = scene.resample(areadef)

    outname = str(outpath / f"{scene.start_time.strftime('%Y%m%d_%H%M%S')}_sentinel2_{rgb_type}_{areadef.area_id}.png")
    print(outname)
    #new_scn.save_dataset(rgb_type, 
    #                     filename=outname)
    new_scn.save_dataset(rgb_type, writer='geotiff',
                         filename=outname[:-3]+'tif')
    return None

    font_size = int(areadef.width / 120)
    from pycoast import ContourWriterAGG
    from PIL import Image, ImageFont, ImageDraw
    # proj4_string = '+proj=stere +lon_0=8.00 +lat_0=50.00 +lat_ts=50.00 +ellps=WGS84'
    # area_extent = (-3363403.31,-2291879.85,2630596.69,2203620.1)
    # area_def = (proj4_string, area_extent)
    # font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf",16)
    import aggdraw
    font_file = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    font_file = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font =  aggdraw.Font('lightgrey', font_file, size=font_size)
    cw = ContourWriterAGG('/home/traceairmass/sat_imagery/')
    # cw.add_coastlines_to_file('BMNG_clouds_201109181715_areaT2.png', area_def, resolution='l', level=4)
    # cw.add_rivers_to_file('BMNG_clouds_201109181715_areaT2.png', area_def, level=5, outline='blue')
    # cw.add_borders_to_file('BMNG_clouds_201109181715_areaT2.png', area_def, outline=(255, 0, 0))

    # >>> cw.add_coastlines(img, area_def, resolution='l', level=4)
    img = Image.open(outname).convert('RGB')
    cw.add_grid(img, areadef, (10.0,10.0),(2.0,2.0), font, write_text=False, fill=pc['gridcolor'],
                outline=pc['gridcolor'], minor_outline=pc['gridcolor'])
    cw.add_shapefile_shapes(img, areadef, 
                            f_coast_o,
                            outline=pc['polycolor'],width=1)

    cw.add_points(img, areadef, points_list=poi_list,
                  ptsize=font_size*0.5,
                  font_file=font_file, font_size=font_size)
    
    draw = ImageDraw.Draw(img)
    print('Font sizes ', font_size, int(font_size*1.8), int(font_size*2.8))
    font = ImageFont.truetype(font_file, size=font_size)
    font18 = ImageFont.truetype(font_file, size=int(font_size*1.8))
    font28 = ImageFont.truetype(font_file, size=int(font_size*2.6))
    w, h = img.size
    draw.text((w*0.98, h*0.99), coast_citation, pc['polycolor'],
              font=font, anchor="rd")
    draw.text((w*0.01, h*0.01), f"{sat} {rgb_type}", 
              (240,248,255), stroke_width=2, stroke_fill='black',
              font=font18, anchor="lt")
    draw.text((w*0.5, h*0.015), scene.start_time.strftime('%Y-%m-%d %H:%M') + "Z", 
              (240,248,255), stroke_width=2, stroke_fill='black',
              font=font28, anchor="mt")
    print('saved to ', outname)
    img.save(outname)
    rgb_img = img.convert("RGB")
    rgb_img.save(outname[:-3]+'jpg', quality=95, subsampling=0)

    

sat = 'Sentinel2'
# python3 ^Cot_image_sentinel.py data_sentinel2/20230408/
p = f"data_sentinel2/{args.date}"

print('Path list', list(Path(p).glob('*')))
files = find_files_and_readers(
        base_dir=p, 
        #start_time=datetime(2022, 12,25),
        #end_time=datetime(2023, 1, 5),
        reader='msi_safe')
print(files)
scene = Scene(filenames=files)
plot_path = Path('plots/') 
print(scene.available_composite_names())
#for rgb_type in ['false_color', 'true_color', 'natural_color']:
for rgb_type in ['false_color', 'true_color', 'true_color_sharp']:
    c = composites[rgb_type]
    plot_path.mkdir(parents=True, exist_ok=True)
    plot_scene(scene, sat, rgb_type, areadef, plot_path, c)
    
