# Glider T-S profiles data viewer

The Glider data viewer is a python command line tool to generate interactive bokeh graphs of glider missions from netCDF files. The generated plots are stored in a html file and are based on the information available in the THREDDS Data Server (TDS) Catalog managed by SOCIB.

The overall purpose of this tool is to visually identify erroneous profiles within the T-S diagram and to offer the possibility to further investigate single profiles.

## Highlights
- Interactive Temperature Salinity Diagrams:
  - casual diagram without any hover effects / color scaling 
  - linear or logarithmic scaled colormapped diagrams based on specified variable(s) - useful to get  visually the profile index for further investigation of single profiles
- Interactive viewer for all single T-S profiles
- Specifying single profiles with selectable x and y axes
- configuration allows to process only single profiles

## Example output
Note that due to the scope of error identification, we are choosing a glider mission with suspicous data:

T-S diagram

![](/img/ts_diagram.png?raw=true "HTML bokeh output")

Linear scaled T-S density diagram

![](/img/ts_diagram_density.png?raw=true "HTML bokeh output")

All profiles viewer

![](/img/all_profiles.png?raw=true "HTML bokeh output")

Single profiles viewer

![](/img/single_profile.png?raw=true "HTML bokeh output")

You can also try the interactive single profile example here:

<a href="http://htmlpreview.github.io/?https://github.com/kriete/gliderT-S_viewer/blob/master/example/single_profile.html">Rendered HTML</a>

## Dependencies
- numpy
- pandas
- bokeh
- matplotlib
- netCDF4

The package has been developed and tested using Ubuntu 14 and is currently only supported by python 2.7.

## Install & Usage
Clone this repository using git and run 

`pip install -r requirement.txt`

to install the python packages or install them manually.

Last but not least, after configurating (see next section), start the processing by running the gliderViewer.py:

 `python gliderViewer.py`

## Configuration
To specify the behaviour, variables as well as the input and output sources, modify the config.ini.

The configuration is devided into two parts: General and Scientifical.
- General
  - project_name: name of the output folder
  - link: link to the input netCDF file (L1 or L2 data possible)
  - output_directory: basic path to the output folder (subfolder will be generated for each project)
  - plot_single_profiles_only: Flag for True or False to process only single profiles as specified in the Scientifical section, or run the whole processing chain
- Scientifical
   - temperature_salinity_range: string array with the variable names for the colormapped T-S diagrams
   - profile_viewer_variables: string array with the variable names to be used as selection for x and y axes for the single profiles processing
   - profile_viewer_profiles: number array with the profile indices for the single profiles processing
