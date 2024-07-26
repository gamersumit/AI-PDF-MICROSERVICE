from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from overlay.service import PDFService, TextOverlay

# Create your views here.
class TextOverlayAndPdfView(generics.CreateAPIView):
    def post(self, request):
        try :
            story = request.data
            
            # start adding text overaly and update pdf url
            story['pages'] = TextOverlay().overlay_illustrations(story['pages'])
            # story['pages'] = TextOverlay().text_overlay(story['pages'])
            
            #gnerate pdf
            pdf_url = PDFService.generate_pdf(
                illustrations=story['pages'],
                title=story['title'],
                )
            
            # update pdf_url
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