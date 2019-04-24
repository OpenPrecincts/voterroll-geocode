import csv
from django.core.management.base import BaseCommand
from ...models import VoterRecord

class Command(BaseCommand):
    help = "Geocode voterroll records"

    def add_arguments(self, parser):
        parser.add_argument("roll", type=int)

    def handle(self, *args, **options):
        fieldnames = [f.name for f in VoterRecord._meta.fields]
        fieldnames.remove("roll")
        fieldnames.append("roll_id")
        with open(f"export-{options['roll']}.csv", "w") as f:
            out = csv.DictWriter(f, fieldnames)
            out.writeheader()

            for n, item in enumerate(VoterRecord.objects.filter(roll_id=options["roll"]).values()):
                if n % 1000 == 0:
                    print(n)
                out.writerow(item)
