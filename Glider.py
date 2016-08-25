import json
import numpy as np
from datetime import datetime

from glider_utils import *
from netCDF4 import Dataset
from bokeh.io import output_file, save
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
        self.plot_only_single_profiles = False
        if read_value_config(self.general_section, 'plot_single_profiles_only') == 'True':
            logger.info('Plotting only single profiles.')
            self.plot_only_single_profiles = True
        self.is_l2 = is_l2_processing_level(self.config[self.general_section]['link'])
        self.read_netcdf_file()
        self.out_dir = self.config[self.general_section]['out_dir'] + self.config[self.general_section]['name']
        create_folder(self.out_dir)
        if not self.plot_only_single_profiles:
            self.create_temperature_salinity_diagram()
            self.create_all_profiles_viewer()
            self.create_single_profiles_viewer()
        else:
            self.create_single_profiles_viewer()

    def read_config(self):
        self.config[self.general_section] = {
            'name': read_value_config(self.general_section, 'project_name'),
            'link': read_value_config(self.general_section, 'link'),
            'out_dir': read_value_config(self.general_section, 'output_directory')
        }
        self.config[self.scientific_section] = {
            't_s_range': map(str, json.loads(read_value_config(self.scientific_section, 'temperature_salinity_range'))),
            # 'full_prof_vars': map(str, json.loads(read_value_config(self.scientific_section, 'full_profiles_variables'))),
            'prof_vars': map(str, json.loads(read_value_config(self.scientific_section, 'profile_viewer_variables'))),
            'prof_numbers': map(float, json.loads(read_value_config(self.scientific_section, 'profile_viewer_profiles')))
        }

    def read_netcdf_file(self):
        try:
            logger.info('Reading dataset...')
            self.root = Dataset(self.config[self.general_section]['link'])
        except (RuntimeError, IOError):
            logger.error('Cannot read dataset {0}.'.format(self.config[self.general_section]['link']))
        self.time = get_data_array(self.root['time'])
        self.depth = get_data_array(self.root['depth'])
        # read_variables = np.union1d(self.config['Scientifical']['full_prof_vars'],
        #                             self.config['Scientifical']['prof_vars'])
        # read_variables = np.union1d(read_variables, self.config[self.scientific_section]['t_s_range'])
        # logger.info('Read variables of interest...')
        # for cur_var in read_variables:
        #     try:
        #         self.variable_data_interest[cur_var] = get_data_array(self.root[cur_var])
        #     except IndexError:
        #         logger.warning('Variable {0} not found.'.format(cur_var))

    def get_depth_levels(self, variable_data):
        if self.is_l2 & (len(variable_data) == len(self.depth)):
            non_flatted_size = len(self.time)
            variable_levels_size = len(self.depth)
            depth_levels = np.zeros((non_flatted_size, variable_levels_size))
            for i in range(0, non_flatted_size):
                depth_levels[i, :] = variable_data
            return depth_levels
        else:
            return variable_data

    def get_time_levels(self, variable_data):
        if self.is_l2 & (len(variable_data.flatten()) == len(self.time)):
            time_levels = np.zeros((len(self.time), len(self.depth)))
            for i in range(0, len(self.time)):
                time_levels[i, :] = variable_data[i]
            return time_levels
        else:
            return variable_data

    def create_temperature_salinity_diagram(self):
        logger.info('Creating TS diagram...')

        depth_levels = self.get_depth_levels(self.depth)
        profile_index = self.get_time_levels(get_data_array_filled_with_nans(self.root['profile_index']))
        latitute = self.get_time_levels(get_data_array_filled_with_nans(self.root['latitude']))
        longitude = self.get_time_levels(get_data_array_filled_with_nans(self.root['longitude']))
        cur_time = self.get_time_levels(get_data_array_filled_with_nans(self.root['time']))
        date_converted = [datetime.fromtimestamp(ts) for ts in cur_time.flatten()]
        converted_time = get_pandas_timestamp_series(date_converted)

        temp = get_data_array_filled_with_nans(self.root['temperature'])
        sal = get_data_array_filled_with_nans(self.root['salinity'])
        p = plot_temperature_salinity_diagram(sal, temp, converted_time, latitude=latitute, longitude=longitude,
                                              profile_index=profile_index,
                                              title_label=self.config[self.general_section]['name'] + ' ' +
                                                          '.html T-S Diagram',
                                              x_label=self.root['salinity'].units,
                                              y_label=self.root['temperature'].units, depth=depth_levels)
        logger.info('Saving TS diagram...')
        output_file(self.out_dir + '/T_S_diagram.html')
        save(p)

        for cur_range_var_name in self.config[self.scientific_section]['t_s_range']:
            try:
                ts_variable = self.root[cur_range_var_name]
            except IndexError:
                ts_variable = np.asarray([])
            t_s_range = get_data_array_filled_with_nans(ts_variable)
            p = plot_temperature_salinity_diagram(sal, temp, converted_time, z=t_s_range, latitude=latitute,
                                                  longitude=longitude, profile_index=profile_index,
                                                  title_label=self.config[self.general_section]['name'] + ' ' +
                                                              '.html T-S Diagram ' + cur_range_var_name,
                                                  x_label=self.root['salinity'].units,
                                                  y_label=self.root['temperature'].units, depth=depth_levels,
                                                  z_label=cur_range_var_name)
            logger.info('Saving TS diagram with ranges {0}...'.format(cur_range_var_name))
            output_file(self.out_dir + '/T_S_diagram_' + cur_range_var_name + '.html')
            save(p)

    def create_single_profiles_viewer(self):
        logger.info('Creating single profiles...')
        for cur_profile in self.config[self.scientific_section]['prof_numbers']:
            logger.info('Processing profile number ' + str(cur_profile))
            data = dict()

            idx = self.get_time_levels(get_data_array_filled_with_nans(self.root['profile_index'])).flatten() == cur_profile
            if idx.any():
                t_non_nan_idx = ~np.isnan(get_data_array_filled_with_nans(self.root['temperature']).flatten()[idx])
                for cur_var_name in self.config[self.scientific_section]['prof_vars']:
                    if cur_var_name == 'depth':
                        cur_data = self.get_depth_levels(get_data_array_filled_with_nans(self.root[cur_var_name])).flatten('A')[idx]
                    else:
                        cur_data = self.get_depth_levels(get_data_array_filled_with_nans(self.root[cur_var_name])).flatten()[idx]
                    data[cur_var_name] = cur_data[t_non_nan_idx]
                plot_single_profile_viewer(self.out_dir + '/single_profile_' + str(cur_profile).replace('.', '_'), **data)
            else:
                logger.info('No profile found for index {0}.'.format(cur_profile))

    def create_all_profiles_viewer(self):
        logger.info('Creating all profile viewer...')
        profiles = self.get_time_levels(get_data_array_filled_with_nans(self.root['profile_index'])).flatten()
        temperature = get_data_array_filled_with_nans(self.root['temperature']).flatten()
        salinity = get_data_array_filled_with_nans(self.root['salinity']).flatten()
        plot_multiple_profiles(self.out_dir + '/all_profiles', temperature, salinity, profiles)