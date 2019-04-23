from django.contrib.gis.db import models


class VoterRoll(models.Model):
    state = models.CharField(max_length=2)
    source = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.state} - {self.source}"


class VoterRecord(models.Model):
    roll = models.ForeignKey(
        VoterRoll, related_name="records", on_delete=models.PROTECT
    )
    source_id = models.CharField(max_length=40)
    address1 = models.CharField(max_length=300)
    address2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)  # for zip+4
    precinct_id = models.CharField(max_length=20)
    precinct_name = models.CharField(max_length=100)

    geocode_attempts = models.PositiveIntegerField(default=0)
    latest_geocode_time = models.DateTimeField(null=True)
    latest_geocode_result = models.CharField(
        max_length=1,
        choices=(
            ("G", "Geocoded"),
            ("X", "No Result From Geocoder"),
            (" ", "No Attempt"),
        ),
        default=" ",
    )
    geocoded_address = models.CharField(max_length=300, blank=True)
    geocode_is_exact = models.BooleanField(default=False)
    coordinates = models.PointField(null=True)
    tiger_line = models.CharField(max_length=20, blank=True)
    tiger_side = models.CharField(max_length=2, blank=True)
    county_fips = models.CharField(max_length=4, blank=True)
    tract = models.CharField(max_length=8, blank=True)
    block = models.CharField(max_length=8, blank=True)

    class Meta:
        indexes = [models.Index(fields=["state", "latest_geocode_result"])]


class County(models.Model):
    state_fips = models.CharField(max_length=2)
    county_fips = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    poly = models.MultiPolygonField()

    def __str__(self):
        return self.name
