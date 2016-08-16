from collections import OrderedDict

import numpy as np
import matplotlib.cm as cm
from matplotlib import colors as mp_colors
from bokeh.plotting import figure
import pandas as pd
from bokeh.models import Plot, Rect, Range1d, Text, ColumnDataSource, HoverTool
from bokeh.layouts import column, row, widgetbox
from bokeh.io import gridplot
import ConfigParser
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('utils.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s p%(process)s {%(pathname)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def plot_single_profile_viewer():
    pass


def get_variable_data(root, variable_name):
    try:
        return get_data_array(root[variable_name])
    except IndexError:
        return np.asarray([])


def get_data_color_palette(data, colormap_name):
    colormap = cm.get_cmap(colormap_name)
    bokeh_palette = [mp_colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]
    data_min = np.nanmin(data)
    data_max = np.nanmax(data)
    logger.info('Color palette min {0} and max {1}'.format(data_min, data_max))
    abs_range = abs(data_min) - abs(data_max)
    abs_range = abs(abs_range) / 256.0
    color_list = np.zeros(shape=(len(data), 1), dtype=object)
    counter = 0
    for _ in data:
        color_list[counter] = ""
        counter += 1
    counter = 1
    lower_limit = data_min
    for i in bokeh_palette:
        upper_limit = data_min + abs_range*counter
        test = np.where((data >= lower_limit) & (data <= upper_limit))
        color_list[test] = i
        counter += 1
        lower_limit = upper_limit
    return color_list, bokeh_palette


def get_data_array_filled_with_nans(data_variable):
    """

    :type data_variable: netCDF4.Dataset
    """
    try:
        fill_value = data_variable._FillValue
    except AttributeError:
        return np.asarray([])
    data_variable = get_data_array(data_variable)
    idx = np.where(data_variable == fill_value)
    data_variable[idx] = np.nan
    return data_variable


def get_pandas_timestamp_series(datetime_array):
    out = pd.Series(np.zeros(len(datetime_array)))
    counter = 0
    for i in datetime_array:
        out[counter] = pd.tslib.Timestamp(i)
        counter += 1
    return out


def plot_temperature_salinity_diagram(x, y, conv_time, colormap_name='winter', title_label='', x_label='', y_label='',
                                      z=np.asarray([]), depth=np.asarray([]), latitude=np.asarray([]),
                                      longitude=np.asarray([]), profile_index=np.asarray([]), z_label=''):
    # [x_data, y_data, z_data] = map(get_data_array_filled_with_nans, [x, y, z])
    fig = figure(title=title_label, tools=["pan, box_zoom, wheel_zoom, save, reset, resize, hover"], webgl=True)
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    depth = depth.flatten()
    longitude = longitude.flatten()
    latitude = latitude.flatten()
    profile_index = profile_index.flatten()
    fig.xaxis.axis_label = x_label
    fig.yaxis.axis_label = y_label
    if np.any(z):
        idx = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z)
        conv_time = conv_time[idx]
        time_strings = map(str, conv_time)
        [x, y, z, depth, latitude, longitude, profile_index] = [x[idx], y[idx], z[idx], depth[idx], latitude[idx],
                                                                longitude[idx], profile_index[idx]]
        data_source = ColumnDataSource(
            data=dict(
                x=x,
                y=y,
                z=z,
                depth=depth,
                lat=latitude,
                lon=longitude,
                prof_idx=profile_index,
                time=time_strings
            )
        )
        z_color_list, bokeh_palette = get_data_color_palette(z, colormap_name)
        fig.scatter(x='x', y='y', fill_color=z_color_list[:, 0], radius=0.006, fill_alpha=0.5,
                    line_color=None, source=data_source, name="data")
        hover = fig.select(dict(type=HoverTool))
        hover.names = ["data"]
        hover.tooltips = OrderedDict([
            ('salinity', '@x{0.0}'),
            ('temperature', '@y{0.0}'),
            (z_label, '@z{0.0}'),
            ('depth', '@depth{0.0}'),
            ('latitude', '@lat{6.4}'),
            ('longitude', '@lon{6.4}'),
            ('profile_index', '@prof_idx{0.0}'),
            ('time', '@time')
        ])
    else:
        idx = ~np.isnan(x) & ~np.isnan(y)
        fig.scatter(x[idx], y[idx], radius=0.006, fill_alpha=0.5, line_color=None)
    return fig


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def read_value_config(section, variable):
    config_handler = ConfigParser.ConfigParser()
    config_handler.read(os.getcwd() + '/config.ini')
    if config_handler.has_section(section):
        return config_handler.get(section, variable)
    else:
        logger.warning('Specified section ' + section + ' not found.')
        return ''


def is_l2_processing_level(link):
    if link.find('/L2/') != -1:
        return True
    else:
        return False


def get_data_array(data_array):
    if type(data_array.__array__()) is np.ma.masked_array:
        return data_array.__array__().data
    else:
        return data_array.__array__()
