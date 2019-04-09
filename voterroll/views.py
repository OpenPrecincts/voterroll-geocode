from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db import connection
from .models import VoterRoll, GeocodeResult


def overview(request):
    data = {
        "rolls": list(VoterRoll.objects.all().annotate(
            total_records=Count("records"),
            # geocoded=Count("records", filter=Q(records__geocodes__isnull=False)),
        ).values("id", "state", "source", "total_records")
        )
    }
    return JsonResponse(data)


def roll_status(request, roll_id):
    roll = get_object_or_404(VoterRoll, pk=roll_id)
    records = roll.records.all().count()
    sql = """select count(*) filter (where failed) as failed_count,
                    count(*) filter (where not failed) as geocoded_count
                    from voterroll_geocoderesult gr
                    INNER JOIN voterroll_voterrecord vr ON gr.record_id=vr.id where vr.roll_id=%s"""
    with connection.cursor() as cursor:
        cursor.execute(sql, (roll.id,))
        failed, geocoded = cursor.fetchone()
    data = {
        "state": roll.state,
        "source": roll.source,
        #"records": records,
        "geocoded": geocoded,
        "failed": failed,
        "percent_attempted":  (geocoded + failed) / records * 100,
        "percent_done": geocoded / records * 100,
    }

    if geocoded + failed:
        data["failure_rate"] = failed / (geocoded + failed) * 100

    return JsonResponse(data)
