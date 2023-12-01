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
proj_id = 'EPSG:3031'
area_extent = (-315239.5, 2093800.2999999998, -265239.5, 2143800.3)
#areadefs['ATKAstd'] = AreaDefinition("ATKAstd", "SouthPolarSt", description, proj_id, proj_dict, width, height, area_extent)
areadefs['ATKAstd'] = AreaDefinition("ATKAstd", "SouthPolarSt", description, proj_id, width, height, area_extent)
print(f'ATKAstd current res [m]  {(area_extent[2]-area_extent[0])/width:.2f}, {(area_extent[3]-area_extent[1])/height:.2f}')

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


def plot_scene(scene, sat, rgb_type, areadef, outpath, pc):
    scene.load([rgb_type])
    new_scn = scene.resample(areadef)

    outname = str(outpath / f"{scene.start_time.strftime('%Y%m%d_%H%M%S')}_sentinel2_{rgb_type}_{areadef.area_id}.png")
    print(outname)
    #new_scn.save_dataset(rgb_type, 
    #                     filename=outname)
    new_scn.save_dataset(rgb_type, writer='geotiff',
                         filename=outname[:-3]+'tif')
    

sat = 'Sentinel2'
p = f"data_sentinel2/{args.date}"

print('Path list', list(Path(p).glob('*')))
files = find_files_and_readers(
        base_dir=p, 
        reader='msi_safe')
print(files)
scene = Scene(filenames=files)
plot_path = Path('plots/') 
print(scene.available_composite_names())
for rgb_type in ['false_color', 'true_color', 'true_color_sharp']:
    c = composites[rgb_type]
    plot_path.mkdir(parents=True, exist_ok=True)
    plot_scene(scene, sat, rgb_type, areadef, plot_path, c)
    
