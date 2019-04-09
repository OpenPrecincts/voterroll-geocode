from django.db import transaction
from django.core.management.base import BaseCommand
from voterroll.models import GeocodeResult
import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):

        now = datetime.datetime.utcnow()

        print(GeocodeResult.objects.all().count(), 'to migrate')
        queryset = GeocodeResult.objects.all().order_by("id").select_related("record")[:50000]

        with transaction.atomic():
            for i, gr in enumerate(queryset):
                print(i)
                rec = gr.record
                rec.geocode_attempts += 1
                rec.latest_geocode_time = now
                if gr.failed:
                    rec.latest_geocode_result = 'X'
                else:
                    rec.latest_geocode_result = 'G'
                    rec.geocoded_address = gr.geocoded_address
                    rec.geocode_is_exact = gr.is_exact
                    rec.coordinates = gr.coordinates
                    rec.tiger_line = gr.tiger_line
                    rec.tiger_side = gr.tiger_side
                    rec.county_fips = gr.county_fips
                    rec.tract = gr.tract
                    rec.block = gr.block
                rec.save()
                gr.delete()
