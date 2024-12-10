# ModisClient

## Overview

`ModisClient` is a Python class designed to interact with the MODIS REST API. It provides common methods to assist with extracting data for a specific product. Valid products can be found on: https://modis.ornl.gov/rst/api/v1/products

## Features

## Usage

### Connecting to the MODIS REST API

To connect to the MODIS REST API you only need to create a client class and use the provided methods.

```python
from msftoolbox.modis.data import ModisClient

modis_client = ModisClient(
    product="modis_product_name",
    longitude="longitude_of_point_of_interest",
    latitude="latitude_of_point_of_interest",
)
```

### Methods

- get_modis_product_dates: returns list of valid dates for given MODIS product
- get_modis_product_bands: returns list of data layer bands available for download
- get_modis_product_data: returns a subset of product data filtered by:
  - latitude: latitude in decimal degrees in geographic Lat/Long WGS 84 coordinate system
  - longitude: longitude in decimal degrees in geographic Lat/Long WGS 84 coordinate system
  - startDate: composite date (AYYYYDDD) start of the subset period. Valid start date is retrieved through get_modis_product_dates method.
  - endDate: composite date (AYYYYDDD) end of the subset period. Valid end date is retrieved through get_modis_product_dates method.

## References

- [MODIS Website](https://modis.ornl.gov/)

## Contributors
- [Jan Swart](https://github.com/jhswart) on behalf of [Equal Experts](https://www.equalexperts.com/)

