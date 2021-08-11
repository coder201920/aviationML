from aviationML.settings import BASE_DIR
from schedule import Scheduler
import threading
import time
import requests
import gzip
import csv
import os
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import sqlite3
from sqlite3 import Error


def connect_to_db(db_file):
    sqlite3_conn = None
    try:
        sqlite3_conn = sqlite3.connect(db_file)
        return sqlite3_conn
    except Error as err:
        print(err)
        if sqlite3_conn is not None:
            sqlite3_conn.close()


def insert_data(df, tablename):
    DB_FILE_PATH = os.path.join(BASE_DIR,'db.sqlite3')
    conn = connect_to_db(DB_FILE_PATH)
    if conn is not None:
        c = conn.cursor()
        df.to_sql(name=tablename, con=conn, if_exists='replace', index=False)
        print(tablename, " data inserted!")
        conn.close()
    else:
        print("DB connection Failed! ",tablename, " data not inserted!")


def extract_airports():
    airportspath = "https://ourairports.com/data/airports.csv"
    filename = os.path.join(BASE_DIR, 'data/AIRPORTS.csv') 
    try:
        csvout = requests.get(url = airportspath).content
        rows = str(csvout.decode("utf-8")).replace('"', '')
        f = open(filename, 'w')
        f.write(rows)
        f.close()
        print(filename+": File extracted")
    except:
        print("Extraction job failed for "+filename)


def extract_taf():
    tafpath = "https://www.aviationweather.gov/adds/dataserver_current/current/tafs.cache.csv.gz"
    filename = os.path.join(BASE_DIR, 'data/TAF.csv') 
    try:
        raw = requests.get(url = tafpath)
        csvout = gzip.decompress(raw.content)
        rows = str(csvout.decode("utf-8"))
        rows_str = "".join(rows)
        f = open(filename, 'w')
        f.write(rows_str)
        f.close()
        print(filename+": File extracted")
    except:
        print("Extraction job failed for "+filename)


def update_airports():
    filename = os.path.join(BASE_DIR, 'data/AIRPORTS.csv')  
    header= ["id","ident","type","name","latitude_deg","longitude_deg","elevation_ft","continent","iso_country","iso_region","municipality","scheduled_service","gps_code","iata_code","local_code","home_link","wikipedia_link","keywords"]
    try:
        df = pd.read_csv(filename, skiprows=1, error_bad_lines=False, header=None, names=header ,low_memory=False, quoting=csv.QUOTE_NONE)
        data_columns = ['latitude_deg', 'longitude_deg']
        num_df = (df.drop(data_columns, axis=1).join(df[data_columns].apply(pd.to_numeric, errors='coerce')))
        final_df = num_df.dropna(subset=['latitude_deg', 'longitude_deg'])
        insert_data(final_df, 'aviationapp_airports')
    except:
        print("Update Airports table failed")

  
def update_taf():
    filename = os.path.join(BASE_DIR, 'data/TAF.csv') 
    header = ["raw_text","station_id","issue_time","bulletin_time","valid_time_from","valid_time_to","remarks","latitude","longitude","elevation_m","fcst_time_from_1","fcst_time_to_1","change_indicator_1","time_becoming_1","probability_1","wind_dir_degrees_1","wind_speed_kt_1","wind_gust_kt_1","wind_shear_hgt_ft_agl_1","wind_shear_dir_degrees_1","wind_shear_speed_kt_1","visibility_statute_mi_1","altim_in_hg_1","vert_vis_ft_1","wx_string_1","not_decoded_1","sky_cover_1_1","cloud_base_ft_agl_1_1","cloud_type_1_1","sky_cover_1_2","cloud_base_ft_agl_1_2","cloud_type_1_2","sky_cover_1_3","cloud_base_ft_agl_1_3","cloud_type_1_3","turbulence_intensity_1","turbulence_min_alt_ft_agl_1","turbulence_max_alt_ft_agl_1","icing_intensity_1","icing_min_alt_ft_agl_1","icing_max_alt_ft_agl_1","valid_time_1_4","sfc_temp_c_1_4","max_or_min_temp_c_1_4","valid_time_1_5","sfc_temp_c_1_5","max_or_min_temp_c_1_5","fcst_time_from_2","fcst_time_to_2","change_indicator_2","time_becoming_2","probability_2","wind_dir_degrees_2","wind_speed_kt_2","wind_gust_kt_2","wind_shear_hgt_ft_agl_2","wind_shear_dir_degrees_2","wind_shear_speed_kt_2","visibility_statute_mi_2","altim_in_hg_2","vert_vis_ft_2","wx_string_2","not_decoded_2","sky_cover_2_1","cloud_base_ft_agl_2_1","cloud_type_2_1","sky_cover_2_2","cloud_base_ft_agl_2_2","cloud_type_2_2","sky_cover_2_3","cloud_base_ft_agl_2_3","cloud_type_2_3","turbulence_intensity_2","turbulence_min_alt_ft_agl_2","turbulence_max_alt_ft_agl_2","icing_intensity_2","icing_min_alt_ft_agl_2","icing_max_alt_ft_agl_2","valid_time_2_4","sfc_temp_c_2_4","max_or_min_temp_c_2_4","valid_time_2_5","sfc_temp_c_2_5","max_or_min_temp_c_2_5","fcst_time_from_3","fcst_time_to_3","change_indicator_3","time_becoming_3","probability_3","wind_dir_degrees_3","wind_speed_kt_3","wind_gust_kt_3","wind_shear_hgt_ft_agl_3","wind_shear_dir_degrees_3","wind_shear_speed_kt_3","visibility_statute_mi_3","altim_in_hg_3","vert_vis_ft_3","wx_string_3","not_decoded_3","sky_cover_3_1","cloud_base_ft_agl_3_1","cloud_type_3_1","sky_cover_3_2","cloud_base_ft_agl_3_2","cloud_type_3_2","sky_cover_3_3","cloud_base_ft_agl_3_3","cloud_type_3_3","turbulence_intensity_3","turbulence_min_alt_ft_agl_3","turbulence_max_alt_ft_agl_3","icing_intensity_3","icing_min_alt_ft_agl_3","icing_max_alt_ft_agl_3","valid_time_3_4","sfc_temp_c_3_4","max_or_min_temp_c_3_4","valid_time_3_5","sfc_temp_c_3_5","max_or_min_temp_c_3_5","fcst_time_from_4","fcst_time_to_4","change_indicator_4","time_becoming_4","probability_4","wind_dir_degrees_4","wind_speed_kt_4","wind_gust_kt_4","wind_shear_hgt_ft_agl_4","wind_shear_dir_degrees_4","wind_shear_speed_kt_4","visibility_statute_mi_4","altim_in_hg_4","vert_vis_ft_4","wx_string_4","not_decoded_4","sky_cover_4_1","cloud_base_ft_agl_4_1","cloud_type_4_1","sky_cover_4_2","cloud_base_ft_agl_4_2","cloud_type_4_2","sky_cover_4_3","cloud_base_ft_agl_4_3","cloud_type_4_3","turbulence_intensity_4","turbulence_min_alt_ft_agl_4","turbulence_max_alt_ft_agl_4","icing_intensity_4","icing_min_alt_ft_agl_4","icing_max_alt_ft_agl_4","valid_time_4_4","sfc_temp_c_4_4","max_or_min_temp_c_4_4","valid_time_4_5","sfc_temp_c_4_5","max_or_min_temp_c_4_5","fcst_time_from_5","fcst_time_to_5","change_indicator_5","time_becoming_5","probability_5","wind_dir_degrees_5","wind_speed_kt_5","wind_gust_kt_5","wind_shear_hgt_ft_agl_5","wind_shear_dir_degrees_5","wind_shear_speed_kt_5","visibility_statute_mi_5","altim_in_hg_5","vert_vis_ft_5","wx_string_5","not_decoded_5","sky_cover_5_1","cloud_base_ft_agl_5_1","cloud_type_5_1","sky_cover_5_2","cloud_base_ft_agl_5_2","cloud_type_5_2","sky_cover_5_3","cloud_base_ft_agl_5_3","cloud_type_5_3","turbulence_intensity_5","turbulence_min_alt_ft_agl_5","turbulence_max_alt_ft_agl_5","icing_intensity_5","icing_min_alt_ft_agl_5","icing_max_alt_ft_agl_5","valid_time_5_4","sfc_temp_c_5_4","max_or_min_temp_c_5_4","valid_time_5_5","sfc_temp_c_5_5","max_or_min_temp_c_5_5","fcst_time_from_6","fcst_time_to_6","change_indicator_6","time_becoming_6","probability_6","wind_dir_degrees_6","wind_speed_kt_6","wind_gust_kt_6","wind_shear_hgt_ft_agl_6","wind_shear_dir_degrees_6","wind_shear_speed_kt_6","visibility_statute_mi_6","altim_in_hg_6","vert_vis_ft_6","wx_string_6","not_decoded_6","sky_cover_6_1","cloud_base_ft_agl_6_1","cloud_type_6_1","sky_cover_6_2","cloud_base_ft_agl_6_2","cloud_type_6_2","sky_cover_6_3","cloud_base_ft_agl_6_3","cloud_type_6_3","turbulence_intensity_6","turbulence_min_alt_ft_agl_6","turbulence_max_alt_ft_agl_6","icing_intensity_6","icing_min_alt_ft_agl_6","icing_max_alt_ft_agl_6","valid_time_6_4","sfc_temp_c_6_4","max_or_min_temp_c_6_4","valid_time_6_5","sfc_temp_c_6_5","max_or_min_temp_c_6_5","fcst_time_from_7","fcst_time_to_7","change_indicator_7","time_becoming_7","probability_7","wind_dir_degrees_7","wind_speed_kt_7","wind_gust_kt_7","wind_shear_hgt_ft_agl_7","wind_shear_dir_degrees_7","wind_shear_speed_kt_7","visibility_statute_mi_7","altim_in_hg_7","vert_vis_ft_7","wx_string_7","not_decoded_7","sky_cover_7_1","cloud_base_ft_agl_7_1","cloud_type_7_1","sky_cover_7_2","cloud_base_ft_agl_7_2","cloud_type_7_2","sky_cover_7_3","cloud_base_ft_agl_7_3","cloud_type_7_3","turbulence_intensity_7","turbulence_min_alt_ft_agl_7","turbulence_max_alt_ft_agl_7","icing_intensity_7","icing_min_alt_ft_agl_7","icing_max_alt_ft_agl_7","valid_time_7_4","sfc_temp_c_7_4","max_or_min_temp_c_7_4","valid_time_7_5","sfc_temp_c_7_5","max_or_min_temp_c_7_5","fcst_time_from_8","fcst_time_to_8","change_indicator_8","time_becoming_8","probability_8","wind_dir_degrees_8","wind_speed_kt_8","wind_gust_kt_8","wind_shear_hgt_ft_agl_8","wind_shear_dir_degrees_8","wind_shear_speed_kt_8","visibility_statute_mi_8","altim_in_hg_8","vert_vis_ft_8","wx_string_8","not_decoded_8","sky_cover_8_1","cloud_base_ft_agl_8_1","cloud_type_8_1","sky_cover_8_2","cloud_base_ft_agl_8_2","cloud_type_8_2","sky_cover_8_3","cloud_base_ft_agl_8_3","cloud_type_8_3","turbulence_intensity_8","turbulence_min_alt_ft_agl_8","turbulence_max_alt_ft_agl_8","icing_intensity_8","icing_min_alt_ft_agl_8","icing_max_alt_ft_agl_8","valid_time_8_4","sfc_temp_c_8_4","max_or_min_temp_c_8_4","valid_time_8_5","sfc_temp_c_8_5","max_or_min_temp_c_8_5","etc"]
    try:
        taf = pd.read_csv(filename, skiprows=5, error_bad_lines=False, header=None, names=header ,low_memory=False, quoting=csv.QUOTE_NONE)
        taf = taf.iloc[1: , 1:]
        insert_data(taf, 'aviationapp_taf')
    except:
        print("Update TAF table failed")
    

def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run

Scheduler.run_continuously = run_continuously


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every().hour.do(extract_taf)
    scheduler.every().hour.do(update_taf)
    scheduler.every().day.do(extract_airports)
    scheduler.every().day.do(update_airports)
    scheduler.run_continuously()