import numpy as np
import matplotlib.cm as cm
from matplotlib import colors as mp_colors
from bokeh.plotting import figure
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
    abs_range = abs(data_min) + abs(data_max)
    abs_range /= 256.0
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
    return color_list


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


def plot_temperature_salinity_diagram(x, y, colormap_name='winter_r', title_label='', x_label='', y_label='',
                                      z=np.asarray([])):
    # [x_data, y_data, z_data] = map(get_data_array_filled_with_nans, [x, y, z])
    fig = figure(title=title_label, tools=["pan, box_zoom, wheel_zoom, save, reset, resize"], webgl=True)
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    if np.any(z):
        idx = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z)
        [x, y, z] = [x[idx], y[idx], z[idx]]
        z_color_list = get_data_color_palette(z, colormap_name)
        fig.scatter(x, y, fill_color=z_color_list[:, 0], radius=0.0015, fill_alpha=0.5, line_color=None)
    else:
        idx = ~np.isnan(x) & ~np.isnan(y)
        fig.scatter(x[idx], y[idx], radius=0.0015, fill_alpha=0.5, line_color=None)
    fig.xaxis.axis_label = x_label
    fig.yaxis.axis_label = y_label
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
    if link.find('/L2/'):
        return True
    else:
        return False


def get_data_array(data_array):
    if type(data_array.__array__()) is np.ma.masked_array:
        return data_array.__array__().data
    else:
        return data_array.__array__()
