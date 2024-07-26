import cloudinary
import cloudinary.api
from io import BytesIO
from fpdf import FPDF
from django.core.mail import send_mail
from django.conf import settings
import requests
from PIL import Image
import fitz
class MediaUtils:  
    @staticmethod
    def UploadMediaToCloud(media, path, image_name):
        try : 
            # print("media: ", media)
            path = f"story/{path}"
            print("path: ", path)  
            if path == "story/pdf" :
                print("inside pdf upload")
                upload = cloudinary.uploader.upload_large(media, folder = path, public_id=image_name, use_filename = True, resource_type = "auto")
            
            else :
                upload = cloudinary.uploader.upload(media, folder = path, public_id=image_name, use_filename = True, resource_type = "auto")   

            # print("upload ====>", upload)    
            return upload['secure_url']
        
        except Exception as e:
            raise Exception(str(e))
    
    @staticmethod
    def download_image(image_url):
        print("in download img", image_url)
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        print("type of image", type(image))
        # print("image ===>", image)
        return image

class PDFUtils:

    def __init__(self, title, width, height):
        self.pdf = FPDF()
        self.width = width * 0.264583  
        self.height = height * 0.264583 
        self.title = title

    # def compress(self, pdf_bytes):
    #     # Open the original PDF
    #     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    #     compressed_pdf_buffer = BytesIO()

    #     # Save the PDF with a lower quality setting
    #     pdf_document.save(compressed_pdf_buffer, garbage=3, deflate=True, clean=True)
    #     compressed_pdf_buffer.seek(0)

    #     return BytesIO(compressed_pdf_buffer.getvalue())
    
    def add_title_page(self):
        # Add a blank page with a title
        self.pdf.add_page(format=(self.width, self.height))
        self.pdf.set_font("Arial", 'B', 24)
        self.pdf.set_xy(0, self.pdf.h / 2)
        self.pdf.cell(w=self.pdf.w, h=0, txt=self.title, border=0, ln=0, align='C')    
    
    def append_images_to_pdf(self, images):
        # imagelist is the list with all image filenames
        for image in images:
            self.pdf.add_page(format=(self.width, self.height))
            self.pdf.image(image, 0, 0, self.width, self.height) 
        
    def save(self):
        # Output PDF as bytes
        pdf_buffer = BytesIO()
        self.pdf.output(pdf_buffer)
        pdf_buffer.seek(0) 
        pdf_bytes = pdf_buffer.getvalue()

        # Remove null bytes (if any)
        # pdf_bytes = pdf_bytes.replace(b'\x00', b'')

        # return self.compress(BytesIO(pdf_bytes))
        return BytesIO(pdf_bytes)
    
class Mail:
    
    def __init__(self, subject, body, emails):
        self.subject = subject
        self.body = body
        self.emails = emails
    
    
    def send(self):
        
        send_mail(
            self.subject, 
            self.body,
            settings.EMAIL_HOST_USER,
            self.emails,
            fail_silently=False)