'''
IMPORTS
'''

import os, random
import pandas as pd
import reverse_geocoder as rev_geo

'''
DEFINE CLASS
'''

class get_coords():

    def __init__(self,data_directory):
        self.directory = data_directory

    def load_data(self,return_data=True):
        ''' access all files in data directory,
            return only the most recent file
        '''
        file_list = os.listdir(self.directory)

        ''' THIS SORT IS WRONG (but it doesn't matter too much right now) '''
        CSVs = [file for file in file_list
                if ('.csv' and 'geocode' and 'US') in file]

        CSV_dict = {int(file.split('.csv')[0].split('_pull')[-1]):file
                    for file in CSVs}
        max_key = max([k for k in CSV_dict.keys()])
        filename = f"{self.directory}//{CSV_dict[max_key]}"

        '''
        CSVs.sort()
        filename = f"{self.directory}/{CSVs[-1]}"
        '''
        if return_data:
            self.filename = filename
            data = pd.read_csv(filename)
        else:
            data = filename

        return data

    def get_new_coords(self):
        ''' use reverse_geocoder module to extract additional data
            on lat/long coords
        '''
        result_list = []
        long1,lat1,long2,lat2 = self.bounding_box

        for num in range(self.num_iterations):
            lat = random.randint(lat1,lat2) + random.randint(0,100)/100
            long = random.randint(long1,long1) + random.randint(0,100)/100

            coords = lat,long
            result = rev_geo.search(coords)[0]

            row = (lat,long,result['lat'],result['lon'],result['name']
                  ,result['admin1'],result['admin2'],result['cc'])
            result_list.append(row)

            if (num+1) % 100 == 0: print(num+1,end="\r",flush=True)

        cols = ['gps_lat','gps_long','lat','long','city','state','area','country']
        new_data = pd.DataFrame(result_list,columns=cols)

        new_data['state_flag'] = [row if row in self.states else 'None'
                                  for row in new_data['state'].values ]

        return new_data

    def save_data(self,data):
        '''
        '''

        latest_filename = self.load_data(return_data=False)

        try:
            prev_data = pd.read_csv(latest_filename)
            data = pd.concat([prev_data,data],sort=True).reset_index(drop=True)
        except: pass

        data.drop_duplicates(inplace=True)
        counter = int(latest_filename.split('.csv')[0].split('_pull')[-1]) + 1

        new_filename = f"{self.directory}/reverse_US_geocode_results_pull{counter}.csv"
        data.to_csv(new_filename,index=False)

    def add_data(self,bounding_box,states_list,num_iter=100,save=True,load=False):

        self.num_iterations = num_iter
        self.bounding_box   = bounding_box
        self.states = states_list

        new_data = self.get_new_coords()
        if save: self.save_data(new_data)
        if load: self.load_data()
