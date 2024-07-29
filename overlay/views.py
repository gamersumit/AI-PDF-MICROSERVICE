import time
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from overlay.service import PDFService, TextOverlay

# Create your views here.
class TextOverlayAndPdfView(generics.CreateAPIView):
    def post(self, request):
        try :
            story = request.data
            pages, pdf_url = PDFService.generate_and_overlay_pdf(illustrations=story['pages'], title=story['title'])
            # update pdf_url
            story['pages'] = pages
            story['pdf_url'] = pdf_url

            # send_pdf_via_email(pdf_link=url, emails=[request.user.email]) 
            PDFService.send_pdf_via_email(pdf_link = pdf_url) 
            return Response(story, status=200)
           
        except ValidationError as e:
            print(" validation errrrror =====>", str(e))
            return Response({'error' : e.detail}, status = 420)
        
        except Exception as e:
            print("errrrror =====>", str(e))
            return Response({'error' : str(e)}, status = 400)