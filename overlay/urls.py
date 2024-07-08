from django.urls import path
from .views import *

urlpatterns = [
    path('', TextOverlayAndPdfView.as_view(), name = 'overlay_and_pdf_generation'),
]