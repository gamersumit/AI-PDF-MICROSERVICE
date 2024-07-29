import time
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from overlay.service import PDFService
# Create your views here.
class TextOverlayAndPdfView(generics.CreateAPIView):
    def post(self, request):
        try :
            story = request.data
            story = PDFService.generate_and_overlay_pdf(story = story)
           
            # send_pdf_via_email(pdf_link=url, emails=[request.user.email]) 
            PDFService.send_pdf_via_email(pdf_link = story['pdf_url']) 
            return Response(story, status=200)
           
        except ValidationError as e:
            print(" validation errrrror =====>", str(e))
            return Response({'error' : e.detail}, status = 420)
        
        except Exception as e:
            print("errrrror =====>", str(e))
            return Response({'error' : str(e)}, status = 400)