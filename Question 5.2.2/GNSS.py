import pandas as pd
import csv

lat_0=12.990123
log_0=80.223452
r=6378137
df= pd.read_csv('dgps_rover_data.csv')

base_lat=df['Base Latitude (Measured)']
base_log=df['Base Longitude (Measured)']
rover_lat=df['Rover Latitude (Measured)']
rover_log=df['Rover Longitude (Measured)']

lat_corr=[]
log_corr=[]

lat_error=base_lat-lat_0
log_error=base_log-log_0 
df['Rover Latitude (Corrected)']=rover_lat-lat_error
df['Rover Longitude (Corrected)']=rover_log-log_error

df.to_csv('dgps_rover_data_corrected.csv', index=False)


