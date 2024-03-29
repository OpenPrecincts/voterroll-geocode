import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from voterroll.models import VoterRoll, VoterRecord


FIELDS = (
    "source_id",
    "address1",
    "address2",
    "city",
    "statefield",
    "zipcode",
    "precinct_id",
    "precinct_name",
)

BATCH_SIZE = 30000


class Command(BaseCommand):
    help = "Load voter roll data from CSV/TSV file"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("filename")
        parser.add_argument("--source")
        for field in FIELDS:
            parser.add_argument(f"--{field}")

    def handle(self, *args, **options):
        field_map = {options.get(k) or k: k for k in FIELDS}
        records = []
        total = 0

        with transaction.atomic():
            roll = VoterRoll.objects.create(
                state=options["state"], source=options["source"]
            )

            with open(options["filename"]) as f:
                for line in csv.DictReader(f, delimiter="\t"):
                    data = {
                        dbname: line[csvname] for csvname, dbname in field_map.items()
                    }
                    data["state"] = data.pop("statefield")
                    records.append(VoterRecord(roll=roll, **data))

                    if len(records) == BATCH_SIZE:
                        VoterRecord.objects.bulk_create(records, batch_size=1000)
                        total += len(records)
                        print(f"creating {BATCH_SIZE} records, total={total}")
                        records = []

                # create whatever is left
                VoterRecord.objects.bulk_create(records)
                total += len(records)
                print(f"creating {len(records)} records, total={total}")
