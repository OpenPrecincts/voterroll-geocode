from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db import connection
from .models import VoterRoll


def overview(request):
    data = {
        "rolls": list(VoterRoll.objects.all().annotate(
            total_records=Count("records"),
        ).values("id", "state", "source", "total_records")
        )
    }
    return JsonResponse(data)


def roll_status(request, roll_id):
    roll = get_object_or_404(VoterRoll, pk=roll_id)
    records = roll.records.all().count()
    failed = roll.records.filter(latest_geocode_result="X").count()
    geocoded = roll.records.filter(latest_geocode_result="G").count()
    data = {
        "state": roll.state,
        "source": roll.source,
        "records": records,
        "geocoded": geocoded,
        "failed": failed,
        "percent_attempted":  (geocoded + failed) / records * 100,
        "percent_done": geocoded / records * 100,
    }

    if geocoded + failed:
        data["failure_rate"] = failed / (geocoded + failed) * 100

    return JsonResponse(data)
