import json
import numpy as np
from glider_utils import *
from netCDF4 import Dataset
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('glider.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s p%(process)s {%(pathname)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Glider:
    def __init__(self):
        self.root = None
        self.time = []
        self.depth = []
        self.config = dict()
        self.general_section = 'General'
        self.scientific_section = 'Scientifical'
        self.variable_data_interest = dict()
        self.read_config()
        self.read_netcdf_file()
        create_folder(self.config[self.general_section]['out_dir'] + self.config[self.general_section]['name'])
        pass

    def read_config(self):
        self.config[self.general_section] = {
            'name': read_value_config(self.general_section, 'project_name'),
            'link': read_value_config(self.general_section, 'link'),
            'out_dir': read_value_config(self.general_section, 'output_directory')
        }
        self.config[self.scientific_section] = {
            't_s_range': read_value_config(self.scientific_section, 'temperature_salinity_range'),
            'full_prof_vars': map(str, json.loads(read_value_config(self.scientific_section, 'full_profiles_variables'))),
            'prof_vars': map(str, json.loads(read_value_config(self.scientific_section, 'profile_viewer_variables')))
        }

    def read_netcdf_file(self):
        try:
            logger.info('Reading dataset...')
            self.root = Dataset(self.config[self.general_section]['link'])
        except RuntimeError:
            logger.error('Cannot read dataset {0}.'.format(self.config[self.general_section]['link']))
        self.time = get_data_array(self.root['time'])
        self.depth = get_data_array(self.root['depth'])
        read_variables = np.union1d(self.config['Scientifical']['full_prof_vars'],
                                    self.config['Scientifical']['prof_vars'])
        logger.info('Read variables of interest...')
        for cur_var in read_variables:
            self.variable_data_interest[cur_var] = get_data_array(self.root[cur_var])

