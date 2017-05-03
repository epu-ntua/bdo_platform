from aggregator.converters.netcdf4 import NetCDF4Converter

cnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
cnv.write_to_disk()
