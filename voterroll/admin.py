from django.contrib import admin
from .models import VoterRecord


@admin.register(VoterRecord)
class VoterRecordAdmin(admin.ModelAdmin):
    list_display = ("source_id", "roll", "address1", "precinct_name")
