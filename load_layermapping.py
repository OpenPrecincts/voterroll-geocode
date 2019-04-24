from django.contrib.gis.utils import LayerMapping
from voterroll.models import County


County.objects.all().delete()
lm = LayerMapping(
    County,
    "tl_2018_us_county/tl_2018_us_county.shp",
    {
        "state_fips": "STATEFP",
        "county_fips": "COUNTYFP",
        "poly": "POLYGON",
        "name": "NAME",
    },
)
lm.save(verbose=True, strict=True)
