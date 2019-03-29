from django.contrib import admin
from django.urls import path
import voterroll.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("overview/", voterroll.views.overview),
    path("overview/<int:roll_id>/", voterroll.views.roll_status),
]
