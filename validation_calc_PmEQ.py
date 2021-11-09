import xarray as xr
import numpy as np
import pandas as pd
import os

if __name__ == '__main__':

    band_no = int(os.environ['band_no'])

    main_dir = '/g/data/w97/ad9701/p_prob_analysis/temp_files/'
    drght_time_slice = slice('1911-01-01', '2020-05-31')
    drght_name = 'full_record' #'recent_drght'
    drght_dir = main_dir + 'GLM_results_' + drght_name + '/validation/'
    ts_list = [2, 6, 12]
    
    for ts in ts_list:    
        # load the total events and actual exceeded events files (1 for events, 0 for no events)
        total_events_file = 'PmEQ_events/total_required_events_' + str(ts) + 'weeks*.nc'
        exceed_events_file = 'PmEQ_events/events_exceed_thresh_' + str(ts) + 'weeks*.nc'

        ds_total_events_temp = xr.open_mfdataset(drght_dir + total_events_file)
        ds_total_events = ds_total_events_temp.sel(time = drght_time_slice)

        ds_exceed_events_temp = xr.open_mfdataset(drght_dir + exceed_events_file)
        ds_exceed_events = ds_exceed_events_temp.sel(time = drght_time_slice)

        # get GLM results
        glm_dir = main_dir + 'GLM_results_' + drght_name + '/'
        glm_file = 'PminusEQ_results_weeks_2_6_12*.nc'
        ds_glm_temp = xr.open_mfdataset(glm_dir + glm_file)
        ds_glm = ds_glm_temp.sel(time = drght_time_slice, timescale = ts)

        # calculations for probability bands
        band_name = np.linspace(0.1, 0.9, 9).round(2)
        low = np.linspace(0.05, 0.85, 9)
        high = np.linspace(0.15, 0.95, 9)

        for i in [band_no]:   
            # select the GLM estimated probabilities that fall in the band
            sel_prob_band = ds_glm['glm_probability'].where((ds_glm['glm_probability'] >= low[i]) & (ds_glm['glm_probability'] < high[i]))
            out_file = drght_dir + 'PmEQ_results/glm_probability_prob_band' + str(band_name[i]) + '_weeks' + str(ts) + '.nc'
            sel_prob_band.to_netcdf(out_file)

            # get all desired events corresponding to the band
            da_total_events_prob_band = ds_total_events['total_events'].where(sel_prob_band > 0)
            # da_sum_total_events = da_total_events_prob_band.sum('time')
            # out_file = drght_dir + 'PmEQ_results/hist_prob_drought_break_band' + str(band_name[i]) + '.nc'

            # get all events that exceeded thresholds
            da_exceed_events_prob_band = ds_exceed_events['events_exceed_thersh'].where(sel_prob_band > 0)
            # da_sum_exceed_events = da_exceed_events_prob_band.sum('time')

            da_prob_drought_break = (da_exceed_events_prob_band.sum('time')/da_total_events_prob_band.sum('time')).rename('hist_prob')
            out_file = drght_dir + 'PmEQ_results/hist_prob_drought_break_band' + str(band_name[i]) + '_weeks' + str(ts) + '.nc'
            da_prob_drought_break.to_netcdf(out_file)