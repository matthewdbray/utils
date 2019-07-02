#!/usr/bin/env python

import argparse
from cookielib import CookieJar
import datetime
import ftplib
import gribapi as grb
import math
import numpy as np
import os
from pytz import timezone, utc
import pandas as pd
#import matplotlib.pyplot as plt
from time import sleep
import sys
import urllib2
import xlrd

class ProcessMet(object):

    def __init__(self, met_xls, met_rsr_xls, outfile, lat, lon, elevation,
            zone, pull_grib, header=None, tmp_grib_folder=None,
            cleanup_folder=False):
        """
        Initializing the class

        You can set a specific folder to put the grib files in, but it will
        default to ~/tmp_grib_folder.

        If cleanup_folder is True it will remove the files after they have
        been processed.  Declaring it as False will keep the files locally,
        which would be good if you were making several copies of the met for
        testing purposes.
        """
        print "Initialized ProcessMet class\n"
        self.met_total = None
        self.ftp = None
        self.fp = open(outfile, 'w')
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
        self.zone = zone
        self.header = header
        self.tmp_grib_folder = tmp_grib_folder
        self.cleanup_folder = cleanup_folder
        self.pull_grib = pull_grib

    def _incidence(self, jday, hr, mins, secs):
        """
        Determines the zenith and azimuth at a given day for a given latitude
        and logitude.
        """

        DEGTORAD = 0.01745329
        lon = abs(self.lon)

        # Converting longitudue and latitude to degrees from radians
        rad_lat = self.lat * DEGTORAD
        rad_long = self.lon * DEGTORAD
        std = 15 * self.zone  # standard meridian

        # Compute fractional year in radians
        yr_frac = (2.0 * math.pi/365.0) * (jday - 1.0 + (hr - 12.0)/24.0)

        # Estimate the time in munutes and solar declination in radians
        # This should probably be broken up into its component parts for
        # clarity
        eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(yr_frac) -\
                0.032077 * math.sin(yr_frac) - 0.014615 *\
                math.cos(2.0 * yr_frac) - 0.040849 * math.sin(2.0 * yr_frac))

        # Calculate solar declination in radians
        # This should probably be broken up into its component parts for
        # clarity
        solar_decl_rad = (0.006918 - 0.399912 * math.cos(yr_frac) + 0.070257 *\
                math.sin(yr_frac) - 0.006758 * math.cos(2.0 * yr_frac) +\
                0.000907 * math.sin(2.0 * yr_frac) - 0.002697 *\
                math.cos(3.0 * yr_frac) + 0.001480 * math.sin(3.0 * yr_frac))
        solar_decl = solar_decl_rad * 180.0 / math.pi

        # Compute the time offset(hours) and true solar time
        # Longitude is in degrees, zone is hours from UTC
        time_offset = (eqtime + 4.0 * (std - lon))/60.0
        true_solar_time = hr + mins/60.0 + secs/3600.0 + time_offset
        # Calculate hour angle in degrees
        hour_ang = 15.0 * (true_solar_time-12)
        hour_ang_rad = hour_ang * DEGTORAD

        # Calculate the solar zenith angle
        msolar_zenith = math.acos(math.sin(rad_lat) * math.sin(solar_decl_rad)+\
                math.cos(rad_lat) * math.cos(solar_decl_rad) *\
                math.cos(hour_ang_rad))
        solar_zenith = msolar_zenith / DEGTORAD

        # Calculate solar azimuth angle
        solar_azimuth = (math.acos((math.sin(solar_decl_rad) -\
                math.sin(rad_lat) * math.cos(msolar_zenith)) / \
                (math.cos(rad_lat) * math.sin(msolar_zenith))))*180.0/math.pi

        return solar_zenith, solar_azimuth

    def _find_local_copy(self, gribfile):
        """
        Setting up local folder and looking for a local copy of the file
        """

        local_copy = False
        if not self.tmp_grib_folder:
            home = os.path.expanduser('~') # Works in all platforms
            tmp = '/tmp_grib_folder'
            tmp = home+tmp
            if not os.path.exists(tmp):
                os.mkdir(tmp)
                os.chdir(tmp)
            else:
                os.chdir(tmp)
                if os.path.isfile(gribfile):
                    local_copy = True
        else:
            if not os.path.exists(self.tmp_grib_folder):
                os.mkdir(self.tmp_grib_folder)
                os.chdir(self.tmp_grib_folder)
            else:
                os.chdir(self.tmp_grib_folder)
                if os.path.isfile(gribfile):
                    local_copy = True
        return local_copy

    def _retrieve_gid_list(self, gribfile):
        """
        Returns the gid list - the reason such a small routine is in a function
        is there are several times when this may fail and need to have the file
        redownloaded and these steps reperformed.
        """
        # with statement guarantees that an fid.close() is performed
        with open(gribfile) as fid:

            # Get number of data layers from GRIB file (known as messages)
            try:
                message_count = grb.grib_count_in_file(fid)
            except Exception, e:
                # This is when there is an incomplete file in your list - So it
                # will attempt to delete and redownload it
                print str(e)
                return None

            # Get a pointer list to each data layer
            gid_list = [grb.grib_new_from_file(fid) for i in range(message_count)]

        return gid_list

    def _retrieve_grib_file(self, date, header, gribfile):
        """
        Grabs a grib file from the NASA website
        """
        # Grabbing the grib file
        lp = open(gribfile,'wb')
        print "Retrieving grib file %s from NASA site\n" % gribfile

        # Getting into the proper directory
        yr = str(date.year) # Year directory
        day = str("%03d" % date.dayofyear) # Day directory
        #filename = self.ftp.retrbinary('RETR ' + gribfile, lp.write)

        url = header+'/'+yr+'/'+day+'/'+gribfile
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)

        lp.write(response.read())
        # self.ftp.cwd('../../') # Back to the main directory
        lp.close()

    def _extract_from_nasa(self, date):
        """
        Nasa FTP GRIB file reader - Pulls down a grib file locally using ftp
        and extracts the data into our met file format

        Full documentation can be found at:
        http://ldas.gsfc.nasa.gov/nldas/NLDAS2forcing.php

        Data Holding Listings can be found here:
        http://disc.sci.gsfc.nasa.gov/hydrology/data-holdings

        Actual data can be found here:
        ftp://hydro1.sci.gsfc.nasa.gov/data/s4pa/NLDAS/NLDAS_FORA0125_H.002/
        """

        # I believe these are static variables that do not change
        FTPURL='https://hydro1.sci.gsfc.nasa.gov/'
        FTPDIR='data/s4pa/NLDAS/NLDAS_FORA0125_H.002'
        header = FTPURL + FTPDIR

        gribfile = 'NLDAS_FORA0125_H.A%d%02d%02d.%02d00.002.grb' % \
                (date.year, date.month, date.day, date.hour)
        
        # Simple test to see if you're ftp has timed out or closed due to some
        # other reason - Also keeps you from having to reopen it every time
        #if not self.ftp:
            #print "Opening FTP connection"
            # Connecting to the ftp site and going to the relevant directory
            #self.ftp = ftplib.FTP(FTPURL, 'ERDC', 'Erdc3909', timeout=1200)
            #ftp.debug(1)
            #self.ftp.cwd(FTPDIR) # Main directory
        # Giving credientials for urllib2 to have access
        user = 'ERDC'
        passwd = 'Erdc3909'

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "https://urs.earthdata.nasa.gov",
                user, passwd)
        
        cookie_jar = CookieJar()

        opener = urllib2.build_opener(
                urllib2.HTTPBasicAuthHandler(password_manager),
                #urllib2.HTTPHandler(debuglevel=1),
                #urllib2.HTTPSHandler(debuglevel=1),
                urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)

        # Setting up directory and searching for local copy
        local_copy = self._find_local_copy(gribfile)
        if not local_copy:
            self._retrieve_grib_file(date, header, gribfile)

        # Retrieve gid list
        gid_list = self._retrieve_gid_list(gribfile)

        # If you have downloaded an incomplete grib file this will fail and the
        # whole script will fail - so this will attempt to get the file again
        # from the Nasa site.
        try:
            gid = gid_list[-1]
        except:
            os.remove(gribfile)
            self._retrieve_grib_file(date, header, gribfile)
            gid_list = self._retrieve_gid_list(gribfile)
            gid = gid_list[-1]

        #======================================================================
        # FORCING message order for (NLDAS_FORA0125_H.A20140324.0800.002.grb)
        #  determined from grib_dump and *.grb.xml
        #
        # 0, TMP 2m above ground temperature
        # 1, 2-m above ground specific humidity (kg/kg)
        # 2, Surface pressure (Pa)
        # 3, 10-m above ground zonal wind speed (m/s)
        # 4, 10-m above ground meridional wind speed (m/s)
        # 5, LW radiation flux downwards (W/m^2)
        # 6, Fraction of total precipitation that is convective
        # 7, Potential energy (J/kg)
        # 8, Potential evaporation (kg/m^2)
        # 9, Precipitation hourly total (kg/m^2)
        # 10, SW radiation flux downards (W/m^2)
        #======================================================================

        params = []

        # Get the date and time
        grib_date = grb.grib_get(gid, 'dataDate')
        grib_time = grb.grib_get(gid, 'dataTime')

        # Get surface pressure (Pa convert to kPa)
        gid = gid_list[2]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        pressure = nearest.value / 1000.0

        # Get air temperature (K convert to C)
        gid = gid_list[0]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        air_temp_k = nearest.value
        air_temp_c = air_temp_k - 273.15

        # Get specific humidity (kg/kg) to relative humidity (%)
        gid = gid_list[1]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        spec_humidity = nearest.value
        rel_humidity = 0.263 * (pressure*1000) * spec_humidity * \
                ((math.exp((17.67*(air_temp_k-273.15))/(air_temp_k-29.65)))**(-1))
        rel_humidity /= 100  # Turn from percent to ratio

        # Get wind speed (m/s) at 10-m above the ground and convert to 2-m
        gid = gid_list[3]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        zon_windspd = nearest.value
        gid = gid_list[4]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        meri_windspd = nearest.value

        windspdMag10 = math.sqrt(zon_windspd**2 + meri_windspd**2)

        if zon_windspd != 0:
            windspdDir = math.degrees(math.atan2(meri_windspd, zon_windspd))
        else:
            windspdDir = math.degrees(math.pi/2.0*(meri_windspd/abs(meri_windspd)))
        if windspdDir < 0:
            windspdDir += 360
        # Adding parameters
        params.extend((date.dayofyear, date.hour, date.minute))
        params.extend((pressure, air_temp_c, rel_humidity))

        # Convert 10-m to 2-m windspeed (surface area roughness)
        p = 0.34 # Surface roughness for wind speed power law
        h = 10.0 # Elevation (m) where windspeed was measured
        z = 2.0 # Elevation (m) where you want to convert the data to
        windspdMag2 = windspdMag10 / ((h/z)**p)

        # Adding parameters
        params.extend((windspdMag2, windspdDir))

        # Get SW radiation (=Global=Direct, will make Diffuse=0)
        gid = gid_list[10]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        sw_down = nearest.value

        # Get LWIR radiation
        gid = gid_list[5]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        lwir_down = nearest.value

        # Get precipitation hourly total (kg/m^2)
        gid = gid_list[9]
        nearest = grb.grib_find_nearest(gid, self.lat, self.lon)[0]
        precip = nearest.value


        # Global radiation, Shortwave direct, Shortwave diffuse, DWelling LWIR
        met_global = sw_down

        # Getting rid of negative global and direct values
        if met_global < 0:
            met_global = 0
        met_direct = met_global*0.80
        met_diffuse = met_global*0.20  # This is arbritrary right now

        params.extend((precip, met_global, met_direct, met_diffuse, lwir_down))

        # Solar position - zenith and azimuth in degrees
        met_zen, met_azi = self._incidence(date.dayofyear, date.hour, 0, 0)
        params.extend((met_zen, met_azi))

        if self.cleanup_folder:
            os.remove(gribfile)
        self._write_to_file(params)
        print "Processed %s date from NASA grib data" % date


    def _extract_from_metdata(self, date):
        """
        Extracts data from the raw met weather station and puts it in our met
        file format.
        """
        params = []
        # day of year, hour, minute
        #idx = self.met_total.index.get_loc(date) # Finding index location of date
        #met_jday = self.met_total.index[idx].strftime("%j")
        met_jday = date.dayofyear
        met_hr = date.hour
        met_min = date.minute
        params.extend((met_jday, met_hr, met_min))

        # barometric pressure, air temperature, relative humidity
        try:
            met_kPas = float(self.met_total.loc[date].BP_mbar ) / 10.0
        except:
            print self.met_total.loc[date].BP_mbar
        met_Ta = self.met_total.loc[date].AirT_2M
        met_RH = self.met_total.loc[date].RH_2M / 100.0
        params.extend((met_kPas, met_Ta, met_RH))

        # wind speed, wind direction
        met_winspd = self.met_total.loc[date].Wind_Spd_2M
        met_windir = self.met_total.loc[date].Wind_Dir_2M
        params.extend((met_winspd, met_windir))

        # precip
        met_precip = self.met_total.loc[date].Precip_Tot
        params.append(met_precip)

        # global radiaiton, shortwave direct, shortwave diffuse, downwelling LWIR
        try:  
            # Grabbing the values from the RSR met file
            met_direct = self.met_total.loc[date].Direct
            met_diffuse = self.met_total.loc[date].Diffuse
            met_global = met_direct + met_diffuse

        except:
            # No RSR file so grabbing from the met file
            try:
                met_global = self.met_total.loc[date].PSP_Total
            except:
                print "Likely that both met files have a PSP_Total.  Failing"
                sys.exit()
            
            # Getting rid of negative global values
            if met_global < 0:
                met_global = 0.0
            # Assuming that direct is 80% of global
            met_direct = met_global * 0.8

            # Assuming that diffuse is 20% of global
            met_diffuse = met_global * 0.2



        met_down_lwir = self.met_total.loc[date].PIR_Flux


        params.extend((met_global, met_direct, met_diffuse, met_down_lwir))


        met_zen, met_azi = self._incidence(met_jday, met_hr, met_min,
                date.second)
        params.extend((met_zen, met_azi))
        self._write_to_file(params)
        print "Processed date: %s from raw met file" % date

    def _write_to_file(self, params):
        """
        Writes the met file parameters into the met file format.

        Note that the params must be in a list in the order that you want them
        written to the file. The params variable only needs to contain relevant
        parameters. Parameters are in this order for awk purposes:
        1) Julian Date 2) Hour 3) Minute 4) Barometric Pressure
        5) Air Temperature 6) Relative Humidity 7) Wind Speed 8) Wind Direction
        9) Visibility (Hard Coded) 10) Aerosol HC 11) Precipitation
        12) 13) 14) 15) 16) 17) 18) Cloud Density HC
        19) Global Radiation 20) Shortwave Direct 21) Shortwave diffuse
        22) Downwelling LWIR 23) Zenith (deg) 24) Azimuth (deg)
        """
        #fmt = "%03d %02d %02d %6.2f %5.2f %4.2f %4.2f %5.1f -9.9 10 %4.2f\
        #        0 0.00  0 0.00  0 0.00  0 %6.2f %6.2f %6.2f %6.2f %5.2f %6.2f\n"

        fmt = "{:0>3d} {:0>2d} {:0>2d} {:6.2f} {:5.2f} {:4.2f} {:4.2f} "\
                "{:5.1f} -9.9 10 {:4.2f} 0 0.00  0 0.00  0 0.00  0 {:6.2f} "\
                "{:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f}\n"

        self.fp.write(fmt.format(*params))



    def read_met_files(self, excel_met, excel_met_rsr=None, to_csv=False):
        """
        Reads two raw excel met files, one being an RSR met file
        As of now it is always defaulted to UTC

        Assumes that the format is the same in the excel met files as previous
        met files, so this may need to be adjusted
        """

        # Set timezone of the data - using pytz because of datetime issues
        zulu = timezone('UTC')

        # Reading each book
        book = xlrd.open_workbook(excel_met)
        if excel_met_rsr:
            book_rsr = xlrd.open_workbook(excel_met_rsr)

        # Reading the first sheet from the book
        sheet = book.sheet_by_index(0)
        if excel_met_rsr:
            sheet_rsr = book_rsr.sheet_by_index(0)

        # Reading data from the first met file
        parse_cols = [0]
        parse_cols += [x for x in xrange(5,39)]
        metxls = pd.read_excel(excel_met, sheet.name, header=0, skiprows=[1],
                parse_cols=parse_cols, infer_datetime_format=True, index_col=0,
                na_values=['NAN'])

        # If there are NAN values infer_datetime_format fails
        print type(metxls.index)
        if type(metxls.index) != pd.core.indexes.datetimes.DatetimeIndex:
            metxls = metxls.dropna()
            metxls.index = metxls.index.to_datetime()

        # Specify the datetime format as UTC (zulu) then shift to local
        met = metxls.tz_localize(zulu)

        # Reading data from the RSR met file
        if excel_met_rsr:
            metxls_rsr = pd.read_excel(excel_met_rsr, sheet_rsr.name, header=0,
                    skiprows=[1], parse_cols=[0,5,6], infer_datetime_format=True,
                    index_col=0, na_values=['NAN'])

            #metxls_rsr = pd.read_excel(excel_met_rsr, sheet_rsr.name, header=0,
                    #skiprows=[1], parse_cols=[0,5], infer_datetime_format=True,
                    #index_col=0, na_values=['NAN'])

            if type(metxls_rsr.index) != pd.core.indexes.datetimes.DatetimeIndex:
                metxls_rsr = metxls_rsr.dropna()
                metxls_rsr.index = metxls_rsr.index.to_datetime()

            metxls_rsr.fillna(0, inplace=True)

        # Specify the datetime format as UTC (zulu)
            met_rsr = metxls_rsr.tz_localize(zulu)

        # Merge both data sets into one time series dataset since they are not
        # currently time synced
        
        if excel_met_rsr:
            try:
                print "Trying to concat met files" 
                met_total = pd.concat([met, met_rsr], join='inner', axis=1)
            except:
                print "Concat failed, trying merge"
                met_total = pd.merge(met, met_rsr, how='inner',
                        left_index=True, right_index=True)
        else:
            met_total = met

        print "\nJoined dataset index: ", met_total.index

        # Printing to csv if given that as a parameter
        if to_csv:
            met_total.to_csv('met_total.csv')

        print met_total
        self.met_total = met_total
        return met_total  # Mainly returned for ipython notebook debugging

    def read_met_csv(self, full_met_csv_fname):
        """
        If you saved the met as a csv from previous time you can read it in
        instantly without processinging it.
        """
        met_total = pd.read_csv(full_met_csv_fname, index_col=0,
                infer_datetime_format=True)
        met_total.index = pd.to_datetime(met_total.index, utc=utc)
        met_total = met_total.sort()
        self.met_total = met_total
        print "Reading met from CSV file: %s" % full_met_csv_fname
        return met_total

    def process_data(self, startRange=None, endRange=None, date_range=None,
            freq=None, metdf=None):
        """
        Begin processing the data and writing out to the SWOE file format

        If ranges are left blank it will start from the minimum to the maximum.
        Give the start and end range in MM/DD/YY HH:MM in UTC.

        If date_range is left blank it will be every frequency. This is so we
        can create irregular date ranges for testing.

        Frequency is defaulted to every hour, but can be changed.
        """
        # Make freq 1H by default
        if not freq:
            freq = '1H'


        # Make sure self.met_total is initialized or there is a backup
        #if self.met_total is None & metdf is None:
        #    print "No met information received, it will all be from NASA\n"
        met_total_bool = True
        metdf_bool = True
        if self.met_total is None:
            print "There is no met total! All data from GRIB files."
            met_total_bool = False
        if metdf is None: 
            metdf_bool = False
        if not met_total_bool and not metdf_bool: 
            print "No met information received, it will all be from NASA\n"


        # Check to see if there is a metdf given for more experimental
        # dataframes to make met files from
        try:
            if self.met_total == None  and metdf.any():
                self.met_total = metdf
        except:
            pass


        # Get the maximum of the intial timestamps for each of the files (These
        # have already been localized to zulu)
        if startRange is None:
            # Iterate through the met data until you are on the first hour
            onHour = False
            for i in range(len(self.met_total)):
                if onHour:
                    break
                else:
                    if self.met_total.index[i].minute == 0 & \
                            self.met_total.index[i].second == 0:
                                onHour = True
                                startRange = self.met_total.index[i]
            if not onHour:
                print "Met is not hourly\n"
                sys.exit()
        # If passed as a datetime object
        elif type(startRange) == datetime.datetime:
            startRange = utc.localize(startRange)

        # If passed as a string object
        else:
            fmt = "%m/%d/%Y %H:%M"
            startRange = datetime.datetime.strptime(startRange, fmt)
            startRange = utc.localize(startRange)

        if endRange is None:
            # Iterating through the end to find the last hour in met xls
            onHour = False
            for i in range(len(self.met_total)-1, 0, -1):
                if onHour:
                    break
                else:
                    if self.met_total.index[i].minute == 0 & \
                            self.met_total.index[i].second == 0:
                                onHour = True
                                endRange = self.met_total.index[i]
        # If passed as a datetime object
        elif type(endRange) == datetime.datetime:
            endRange = utc.localize(endRange)

        # If passed a string object
        else:
            fmt = "%m/%d/%Y %H:%M"
            endRange = datetime.datetime.strptime(endRange, fmt)
            endRange = utc.localize(endRange)

        # Create the date range that you want to extract
        print type(date_range)
        if not date_range:
            date_range = pd.date_range(startRange, endRange, freq=freq)

        print "Creating met file from dates %s to %s" % \
                (date_range[0], date_range[-1])

        print "Pulling from GRIB data is: %s" % self.pull_grib
        # Inserting headers into metfile - you can declare a string for the
        # header when you instantiate the class or just leave it blank and use
        # the metfile name as the header
        if self.header:
            self.fp.write(self.header+'\n')
        else:
            try:
                self.fp.write("%s\n" % self.fp.name.split('.')[0])
            except:
                self.fp.write("%s\n" % self.fp.name)

        self.fp.write("Elevation(m), Latitude, Longitude, GMT-UTC\n")
        self.fp.write(str.format("      %6.3f   %6.3f   %7.3f  %d\n") %\
                (self.elevation, self.lat, self.lon, self.zone))

        self.fp.write("Day  Hr Min Press  Temp  Rh  WndSp WDir  Vis Aer Precip"\
              " Cloud data            Global Direct Diffuse  dwn    zen    az\n")
        self.fp.write("             kPa     C       m/s   deg   (km) H  mm   P"\
              "amt  L  amt  M  amt  H  W/m2   W/m2   W/m2    W/m2\n")

        # Set up counters
        from_met = 0
        from_nasa = 0

        # grab the information from the NASA site, and put it into met file
        # format
        for date in date_range:
            try:
                self.met_total.loc[date]
                self._extract_from_metdata(date)
                from_met += 1
            except Exception, e:  # Not in met data
                print "Exception: %s" % e
                if self.pull_grib is True:
                    print "Pulling from Grib"
                    self._extract_from_nasa(date)
                    from_nasa += 1
                else:
                    print "%s will be skipped" % date

        # Closing ftp if it was ever opened
        if self.ftp:
           self.ftp.close()

        # Closing file
        self.fp.close()

        # Print out information
        print "\nProcessed met data from date %s to date %s.\n" % \
                (date_range[0], date_range[-1])
        print "%d hours were from the met station and %d hours were from NASA grib data\n" %\
                (from_met, from_nasa)
        print "It was completed at a frequency of %s" % freq


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    # Necessary arguments
    parser.add_argument('--lat', action='store', type=float,
            dest='lat', required=True, help='The latitude of the location.')
    parser.add_argument('--lon', action='store', type=float,
            dest='lon', required=True, help='The longitude of the lcoation.')
    parser.add_argument('--elevation', action='store', type=float,
            dest='elevation', required=True,
            help='The elevation of the met station')
    parser.add_argument('--zone', '-z', action='store', dest='zone', type=int,
            required=True,
            help='The time zone offset of the site for the met file')

    # Optional arguments
    parser.add_argument('--outfile','-o', action='store', default='test.met',
            dest='outfile_fname', required=False, help='The outfile met name.')
    parser.add_argument('--met', '-m', action='store', type=str,
            dest='met', required=False, default=None,
            help='The met excel file')
    parser.add_argument('--rsr', '-r', action='store', type=str,
            dest='met_rsr', required=False, default=None,
            help='The met rsr excel file')
    parser.add_argument('--start', '-s', action='store', type=str,
            default=None, dest='start_range',
            help='The time you want to start from in MM/DD/YY HH:mm format')
    parser.add_argument('--end', '-e', action='store', type=str,
            default=None, dest='end_range',
            help='The time you want to end with in MM/DD/YY HH:mm format')
    parser.add_argument('--header', action='store', type=str, dest='header',
            required=False, default=None,
            help='This is the header information at the top of the met file')
    parser.add_argument('--folder', '-f', action='store', type=str,
            dest='tmp_grib_folder', required=False, default=None,
            help='This is the folder that will contain your grib files')
    parser.add_argument('--clean', '-c', action='store_true',
            dest='cleanup_folder', required=False, default=None,
            help='Determines whether the program will delete grib files')
    parser.add_argument('--freq', action='store', required=False,
            default=None, type=str, dest='freq',
            help='Gives the frequency in common intervals to grab for the met.')
    parser.add_argument('--csv', action='store', required=False, default=None,
            type=str, dest='csv_file',
            help='The csv file that you dumped of the met pandas dataframe')
    parser.add_argument('--nogrib', '-ng', action='store_false', required=False,
            default=True, dest='pull_grib',
            help='If you include this flag days that are missing will not be'
            'pulled from the GRIB files')


    results = parser.parse_args()

    # Parsing arguments to more easily pass to the function
    met = results.met
    met_rsr = results.met_rsr
    lat = results.lat
    lon = results.lon
    elevation = results.elevation
    zone = results.zone
    outfile_fname = results.outfile_fname
    header = results.header
    if type(header) == list:
        header = ' '.join(header)
    tmp_grib_folder = results.tmp_grib_folder
    if type(tmp_grib_folder) == list:
        tmp_grib_folder = ' '.join(tmp_grib_folder)
    cleanup_folder = results.cleanup_folder
    start_range = results.start_range
    end_range = results.end_range
    freq = results.freq
    csv_file = results.csv_file
    pull_grib = results.pull_grib

    # Instantiate class
    try:
        proc_met = ProcessMet(met, met_rsr, outfile_fname, lat, lon, elevation,
            zone, pull_grib, header,tmp_grib_folder, cleanup_folder)
    except:
        sys.exit()
    # Read met files into one dataframe, if no met is passed it is all grib
    # data being processed
    if met and met_rsr:
        proc_met.read_met_files(met, met_rsr)
    elif met and not met_rsr: 
        proc_met.read_met_files(met)
    elif csv_file:
        proc_met.read_met_csv(csv_file)

    # Process data
    date_range = None
    proc_met.process_data(start_range, end_range, date_range, freq)




