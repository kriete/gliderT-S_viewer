import numpy as np
import matplotlib.cm as cm
from matplotlib import colors as mp_colors
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


def get_data_color_palette(data, colormap_name):
    colormap = cm.get_cmap(colormap_name)
    bokeh_palette = [mp_colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]
    data_min = np.nanmin(data)
    data_max = np.nanmax(data)
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


def plot_temperature_salinity_diagram():
    pass


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
