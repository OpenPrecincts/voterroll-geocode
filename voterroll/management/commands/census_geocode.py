import time
import datetime
import pytz
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction
from voterroll.models import VoterRecord
import censusbatchgeocoder


MAX_CHUNK_SIZE = 10000


def record_to_dict(record):
    return {
        "id": record.id,
        "address": record.address1,
        "city": record.city,
        "state": record.state,
        "zipcode": record.zipcode,
    }


class ChunkedProcessor:
    def get_records(self, state, chunk_size):
        return []

    def process_chunk(self, records):
        """
        process a chunk of records
        returns: #success, #failures
        """
        return


class CensusGeocoder(ChunkedProcessor):
    def __init__(self):
        self.record_map = {}

    def get_records(self, state, chunk_size):
        """ return list of records and {id: record} mapping """
        if chunk_size > MAX_CHUNK_SIZE:
            chunk_size = MAX_CHUNK_SIZE
        qs = list(VoterRecord.objects.filter(state=state, latest_geocode_result=" ")[:chunk_size])

        self.record_map = {r.id: r for r in qs}

        return [record_to_dict(r) for r in qs]

    def process_chunk(self, records):
        results = []
        failures = 0
        now = pytz.utc.localize(datetime.datetime.utcnow())
        results = censusbatchgeocoder.geocode(records)
        with transaction.atomic():
            for result in results:
                # get record to update
                record = self.record_map[result["id"]]
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
        return len(results), failures


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
        processor = CensusGeocoder()
        while processed < options["n"]:
            processed += options["chunk"]
            start = time.time()
            records = processor.get_records(options["state"], options["chunk"])
            elapsed = time.time() - start
            print(f"got {len(records)} in {elapsed}")
            try:
                start = time.time()
                results, failures = processor.process_chunk(records)
                elapsed = time.time() - start
            except Exception as e:
                print(e)
                continue
            print(
                f"saving {results} records, {failures} were non-matched, took {elapsed}"
            )
            total_failures += failures
            total_elapsed += elapsed

        print(
            f"Done! saved a total {processed} records, {total_failures} were non-matched, took {total_elapsed}"
        )
