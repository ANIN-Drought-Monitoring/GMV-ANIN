import json
import os
import datetime
import openeo
import geopandas as gpd
import sys
from openeo_utils.utils import *

connection = get_connection()

SPI_dc = connection.load_collection(
    "AGERA5",
    # temporal_extent=["2015-01-01", "2023-01-01"],  # Small sample date
    # spatial_extent={
    #     "west": 10,
    #     "south": -40,
    #     "east": 40,
    #     "north": -20,
    # },
    bands=["precipitation-flux"],
)
SPI_dc = SPI_dc.aggregate_temporal_period("month", reducer="sum")

# Linearly interpolate missing values. To avoid protobuf error.
SPI_dc = SPI_dc.apply_dimension(
    dimension="t",
    process="array_interpolate_linear",
)
SPI_dc = SPI_dc.rename_labels('bands', ['SPI'])

# SPI_dc = (SPI_dc * 0.01) # Scaling has no impact on Z-score

udf_code = load_udf(os.path.join(os.path.dirname(__file__), "SPI_UDF.py"))
SPI_dc = SPI_dc.apply_dimension(dimension="t", code=udf_code, runtime="Python")

if __name__ == "__main__":
    geojson = load_south_africa_geojson()
    SPI_dc = SPI_dc.filter_spatial(geojson)
    custom_execute_batch(SPI_dc)