# Generated by Django 2.1.7 on 2019-04-10 00:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("voterroll", "0006_auto_20190409_1532")]

    operations = [
        migrations.RemoveField(model_name="geocoderesult", name="record"),
        migrations.DeleteModel(name="GeocodeResult"),
    ]
