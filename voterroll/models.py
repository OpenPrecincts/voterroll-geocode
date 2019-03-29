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


class GeocodeResult(models.Model):
    record = models.ForeignKey(
        VoterRecord, related_name="geocodes", on_delete=models.CASCADE
    )
    failed = models.BooleanField(default=False)
    geocoded_address = models.CharField(max_length=300)
    is_exact = models.BooleanField()
    coordinates = models.PointField(null=True)
    tiger_line = models.CharField(max_length=20)
    tiger_side = models.CharField(max_length=2)
    county_fips = models.CharField(max_length=4)
    tract = models.CharField(max_length=8)
    block = models.CharField(max_length=8)
