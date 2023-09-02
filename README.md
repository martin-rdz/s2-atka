
# Download and plot Sentinel2 images for the ATKA bay


### Setup

```
python3 -m venv s2-env

source s2-env/bin/activate

python3 -m pip install "satpy[msi_safe,rayleigh,angles,geotiff,overlays]"
python3 -m pip install toml
python3 -m pip install matplotlib

mkdir data_sentinel2 
mkdir plots
```


Provide your account information for the [copernicus dataspace](https://dataspace.copernicus.eu/) in `config.toml`.



### Usage

The point of interest, that should be covered by the image is currently hard-coed in `download_sentinel.py`.

```
python3 download_sentinel.py 20230312 -r 5000
python3 plot_image_sentinel.py 20230312
```





### Composites and Projection

A custom true color composite is added in `satpy_config/composites/msi.yaml`:

```
true_color_sharp:
  compositor: !!python/name:satpy.composites.RatioSharpenedRGB
  prerequisites:
  - name: 'B04'
    modifiers: [effective_solar_pathlength_corrected, rayleigh_corrected]
  - name: 'B03'
    modifiers: [effective_solar_pathlength_corrected, rayleigh_corrected]
  - name: 'B02'
    modifiers: [effective_solar_pathlength_corrected, rayleigh_corrected]
  standard_name: true_color_sharp
```

The geotiffs are output with the projection:

```
escription = "ATKAstd in SouthPolarSt"
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
```




