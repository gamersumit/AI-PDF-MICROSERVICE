import cloudinary
import cloudinary.api
from io import BytesIO
from fpdf import FPDF
from django.core.mail import send_mail
from django.conf import settings
import requests
from PIL import Image
import firebase_config
from firebase_admin import storage
from django.core.files.base import ContentFile

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

    def __init__(self, title, image):
        self.pdf = FPDF()
        self.width = image.width * 0.264583  
        self.height = image.height * 0.264583 
        self.title = title
    
    # def add_cover_page(self, image):
    #     overlay =   TextOverlay()
    #     image = overlay.overlay_with_background(image = image, text=self.title, y_axis='center')
    #     # upload the overlayed image to the cloudinary
    #     image_name = self.title+"_cover"
    #     image_url = MediaUtils.UploadMediaToCloud(image, 'text_overlay', image_name)
        
    #     # append the image to pdf
    #     self.append_images_to_pdf([image])

    #     return image_url

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
        

class FirebaseMediaUtils:
    @staticmethod
    def upload_media_to_firebase(media, path, image_name):
        try:
            print("in upload media to firebase")
            bucket = storage.bucket()
            print("bucket... ", bucket)
            blob = bucket.blob(f"{path}/{image_name}")
            print("blob...", blob)
            blob.upload_from_string(media.read(),  content_type='application/pdf')
            print("one...")
            blob.make_public()
            print("two... ")
            print("url:::::::::: ", blob.public_url)
            return blob.public_url
        except Exception as e:

            raise Exception(str(e))