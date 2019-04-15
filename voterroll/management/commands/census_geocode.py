import time
import datetime
import pytz
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction
from voterroll.models import VoterRecord
import censusbatchgeocoder


MAX_CHUNK_SIZE = 10000


def get_records(state, n):
    """ return list of records and {id: record} mapping """
    if n > MAX_CHUNK_SIZE:
        n = MAX_CHUNK_SIZE
    qs = list(VoterRecord.objects.filter(state=state, latest_geocode_result=" ")[:n])
    return [record_to_dict(r) for r in qs], {r.id: r for r in qs}


def record_to_dict(record):
    return {
        "id": record.id,
        "address": record.address1,
        "city": record.city,
        "state": record.state,
        "zipcode": record.zipcode,
    }


def geocode_chunk(records, record_map):
    results = []
    failures = 0
    start = time.time()
    now = pytz.utc.localize(datetime.datetime.utcnow())
    results = censusbatchgeocoder.geocode(records)
    with transaction.atomic():
        for result in results:
            # get record to update
            record = record_map[result["id"]]
            record.geocode_attempts += 1
            record.latest_geocode_time = now

            if result["is_match"] == "Match":
                record.latest_geocode_result = "G"
                record.geocoded_address = result["geocoded_address"]
                record.geocode_is_exact = result["is_exact"] == "Exact"
                record.coordinates = Point(result["longitude"], result["latitude"])
                record.tiger_line = result["tiger_line"]
                record.tiger_side = result["side"]
                record.county_fips = result["county_fips"]
                record.tract = result["tract"]
                record.block = result["block"]
            else:
                failures += 1
                record.latest_geocode_result = "X"
            record.save()
    elapsed = time.time() - start
    return len(results), failures, elapsed


class Command(BaseCommand):
    help = "Geocode voterroll records"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("-n", type=int, default=100000)
        parser.add_argument("--chunk", type=int, default=500)

    def handle(self, *args, **options):
        processed = 0
        total_failures = 0
        total_elapsed = 0
        while processed < options["n"]:
            processed += options["chunk"]
            start = time.time()
            records, record_map = get_records(options["state"], options["chunk"])
            elapsed = time.time() - start
            print(f"got {len(records)} in {elapsed}")
            try:
                results, failures, elapsed = geocode_chunk(records, record_map)
            except Exception as e:
                print(e)
                continue
            print(f"saving {results} records, {failures} were non-matched, took {elapsed}")
            total_failures += failures
            total_elapsed += elapsed

        print(f"Done! saved a total {processed} records, {total_failures} were non-matched, took {total_elapsed}")
