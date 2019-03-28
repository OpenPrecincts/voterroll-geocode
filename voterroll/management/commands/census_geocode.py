from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from voterroll.models import VoterRecord, GeocodeResult
import censusbatchgeocoder


MAX_CHUNK_SIZE = 1000


def get_records(state, n):
    if n > MAX_CHUNK_SIZE:
        n = MAX_CHUNK_SIZE
    return [record_to_dict(r)
            for r in VoterRecord.objects.filter(state=state, geocodes__isnull=True)[:n]]


def record_to_dict(record):
    return {"id": record.id, "address": record.address1, "city": record.city, "state": record.state, "zipcode": record.zipcode}


def geocode_chunk(records):
    results = []
    failures = 0
    for result in censusbatchgeocoder.geocode(records):
        if result["is_match"] == "Match":
            results.append(GeocodeResult(
                record_id=result["id"],
                geocoded_address=result["geocoded_address"],
                is_exact=result["is_exact"] == "Exact",
                coordinates=Point(result["longitude"], result["latitude"]),
                tiger_line=result["tiger_line"],
                tiger_side=result["side"],
                tract=result["tract"],
                block=result["block"],
            ))
        else:
            failures += 1
            results.append(GeocodeResult(
                record_id=result["id"],
                failed=True,
                is_exact=False,
            ))
    print(f"saving {len(results)} records, {failures} were non-matched")
    GeocodeResult.objects.bulk_create(results)


class Command(BaseCommand):
    help = "Geocode voterroll records"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("-n", type=int, default=100000)
        parser.add_argument("--chunk", type=int, default=500)

    def handle(self, *args, **options):
        processed = 0
        while processed < options["n"]:
            processed += options["chunk"]
            records = get_records(options["state"], options["chunk"])
            geocode_chunk(records)