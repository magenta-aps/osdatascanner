from django.urls import path

from . import views

urlpatterns = [
    path(
            "background_job/<uuid:pk>/status",
            views.render_background_job_status_widget,
            name="background_job_status_widget"),
]
