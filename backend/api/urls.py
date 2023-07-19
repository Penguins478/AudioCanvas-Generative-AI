from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('process-audio/', views.process_audio, name='process-audio'),
]
