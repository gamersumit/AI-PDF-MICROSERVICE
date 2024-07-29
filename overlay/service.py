import time 
import os
import numpy as np
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cv2
from utils import Mail, MediaUtils, PDFUtils
from collections import Counter


class PDFService:
    @staticmethod
    def generate_and_overlay_pdf(illustrations, title):
        # fetch first image for the size reference
        image = illustrations[0]
        image = MediaUtils.download_image(image_url= image['image_url'])

        # create a pdf object
        pdf = PDFUtils(title = title, width=image.width, height=image.height)
        pdf.add_title_page()

        # text overlay object
        overlay = TextOverlay()

        for llustration in illustrations :
            # downlaod image
            image = MediaUtils.download_image(image_url= illustration['image_url'])
            
            # overlay text on the image
            image_name = f"{illustration['id']}_page{illustration['page_no']}_text"
            image = overlay.overlay_with_background(image = image, text = illustration['text'])

            # upload the overlayed image to the cloudinary
            image_url = MediaUtils.UploadMediaToCloud(image, 'text_overlay', image_name)
            
            # append the image to pdf
            pdf.append_images_to_pdf([image])
            
            # update overlayed image url in illustration
            illustration['overlay_image_url'] = image_url
        
        #upload pdf to clodinary
        pdf_bytes = pdf.save()
        return illustrations, MediaUtils.UploadMediaToCloud(pdf_bytes, 'pdf', title.strip())

    
    @staticmethod
    def send_pdf_via_email(pdf_link, emails = ['devinnow8@gmail.com']):
        subject = f"Your Requested Story Book PDF"
        body = (
            f"Hello !!,\n\n"
            "We are pleased to inform you that your requested PDF is ready for download. "
            "You can access it using the following link:\n\n"
            f"{pdf_link}\n\n"
            "Thank you for using our service!\n"
            "Best regards,\n"
            "AI BOOK"
        )
        
        message = Mail(
                    subject = subject,
                    body = body,
                    emails = emails
                    )
        
        message.send()


class TextOverlay(): 
    def overlay_with_background(self, image, text):
        print("start ===>")
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Define text and font
        font_path = os.getenv('FONT_PATH')  # Optional: specify a font
        font = ImageFont.truetype(font_path, size=20)  # Adjust size as needed

        lines = self.wrap_text(
            draw=draw, 
            font=font, 
            text = text,
            max_width_pixels=image.width-(image.width/6), 
            )
        
        text = "\n".join(lines)

        

        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x, y = 50, 50  # Adjust as needed

        # Calculate dynamic position based on image size
        image_width, image_height = image.size
        margin = 30  # Adjust as needed
        x = (image_width - text_width) / 2
        y = image_height - text_height - margin

        # Define the background box
        box_padding = 10
        box = [x - box_padding, y - box_padding, x + text_width + box_padding, y + text_height + box_padding]

        # Draw the rounded rectangle
        radius = 20  # Adjust as needed
        draw.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 130))

        # Draw the text on top of the box
        draw.text((x, y), text, font=font, fill="black")  # Adjust fill color as needed

        combined = Image.alpha_composite(image, txt_layer)
        # Save to a BytesIO object
        img_byte_arr = BytesIO()
        combined.save(img_byte_arr, format='PNG', optimize=True, compress_level=9)
        img_byte_arr.seek(0)

        # Return the image as HTTP response
        return img_byte_arr


    def wrap_text(self, text, draw, font, max_width_pixels):
        """
        Wrap text to fit within a specified width in pixels.

        :param text: The text to wrap.
        :param font: The PIL ImageFont object to use for text measurement.
        :param max_width_pixels: The maximum width in pixels.
        :return: A list of wrapped text lines.
        """
        lines = []
        words = text.split(' ')
        current_line = ''

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width_pixels:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
    

    # def wrap_text(self, draw, text, font, max_width):
    #     print("in wrap text")
    #     lines = []
    #     if '\\n' in text:  # Check for \n characters
    #         print("'\n' present...")
    #         paragraphs = text.split('\\n')  # Split text into paragraphs

    #         for paragraph in paragraphs:
    #             words = paragraph.split()
    #             print("words: ", words)

    #             while words:
    #                 line = ""
    #                 while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
    #                     line += words.pop(0) + " "

    #                 # If there are no words left, add the current line and break
    #                 if not words:
    #                     lines.append(line.strip())
    #                     break

    #                 # Check if the current word is too long to fit in an empty line
    #                 word = words.pop(0)
    #                 if draw.textbbox((0, 0), word, font=font)[2] > max_width:
    #                     # Hyphenate the word and add parts to lines
    #                     while word:
    #                         for i in range(1, len(word) + 1):
    #                             if draw.textbbox((0, 0), word[:i], font=font)[2] > max_width:
    #                                 lines.append(word[:i-1] + '-')
    #                                 word = word[i-1:]
    #                                 break
    #                         else:
    #                             lines.append(word)
    #                             word = ""
    #                 else:
    #                     lines.append(line.strip())
    #                     lines.append(word)
    #             lines.append("")  # Add a blank line between paragraphs

    #         # Remove the last empty line added between paragraphs
    #         if lines and lines[-1] == "":
    #             lines.pop()
    #     else:
    #         print("no '\n' present...")
    #         words = text.split()
    #         print("words: ", words)

    #         while words:
    #             line = ""
    #             while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
    #                 line += words.pop(0) + " "

    #             # If there are no words left, add the current line and break
    #             if not words:
    #                 lines.append(line.strip())
    #                 break

    #             # Check if the current word is too long to fit in an empty line
    #             word = words.pop(0)
    #             if draw.textbbox((0, 0), word, font=font)[2] > max_width:
    #                 # Hyphenate the word and add parts to lines
    #                 while word:
    #                     for i in range(1, len(word) + 1):
    #                         if draw.textbbox((0, 0), word[:i], font=font)[2] > max_width:
    #                             lines.append(word[:i-1] + '-')
    #                             word = word[i-1:]
    #                             break
    #                     else:
    #                         lines.append(word)
    #                         word = ""
    #             else:
    #                 lines.append(line.strip())
    #                 lines.append(word)
    #     return lines
        
    # def text_overlay(self, illustrations):        
    #     counter = 0
    #     print("in text overlay")
        
    #     for illustration in illustrations:
    #         print("illustration: ", illustration)
    #         image_id = illustration['id']
    #         print("image id: ", image_id)
    #         image_url = illustration['image_url']
    #         print("image_url: ", image_url)
    #         text_to_be_overlayed = illustration['text']

    #         image = MediaUtils.download_image(image_url)

    #         font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()

    #         print("font_color: ", font_color_detector)
    #         fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
            
    #         font_path = os.getenv('FONT_PATH')
    #         font_size = 41
    #         print("font size")
    #         font = ImageFont.truetype(font_path, font_size)

    #         draw = ImageDraw.Draw(image)
    #         print("draw")
    #         # Set maximum width for wrapping
    #         max_text_width = image.width - 30  
    #         wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
    #         print("wrapped")
    #         # Calculate total height required for wrapped text
    #         total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)

    #         fixed_y = image.height - 135

    #         # Calculate starting y position to center vertically
    #         y = fixed_y - total_text_height // 2

    #         for line in wrapped_text_lines:
    #             if line:  
    #                 text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]

    #                 # Calculate starting x position to center align the line horizontally
    #                 x = (image.width - text_width) // 2

    #                 draw.text((x, y), line, fill=fill, font=font)

    #                 # Move to the next line vertically
    #                 y += text_height

    #         print("done hai uye to")
            
    #         image_bytes = BytesIO()
    #         image.save(image_bytes, format='JPEG')
    #         image_bytes.seek(0)
            
    #         image_name = f"{image_id}_page{counter}_text"
    #         saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
    #         print("img url: ", saved_img_url)
    #         illustration['overlay_image_url'] = saved_img_url
        
    #     return illustrations


# class FontColorForBackgroundDetectorService:
#     def __init__(self, image):
#         self.img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)  # Convert PIL image to NumPy array
#         self.manual_count = {}
#         self.h, self.w, self.channels = self.img.shape
#         self.total_pixels = self.h * self.w

#     def count(self):
#         for y in range(0, self.h):
#             for x in range(0, self.w):
#                 BGR = (self.img[y, x, 0], self.img[y, x, 1], self.img[y, x, 2])
#                 if BGR in self.manual_count:
#                     self.manual_count[BGR] += 1
#                 else:
#                     self.manual_count[BGR] = 1

#     def average_colour(self):
#         red, green, blue = 0, 0, 0
#         sample = 10
#         for top in range(0, sample):
#             blue += self.number_counter[top][0][0]
#             green += self.number_counter[top][0][1]
#             red += self.number_counter[top][0][2]

#         average_red = red / sample
#         average_green = green / sample
#         average_blue = blue / sample
#         print("Average RGB for top ten is: (", average_red, ", ", average_green, ", ", average_blue, ")")
        
#         return (average_red, average_green, average_blue)

#     def twenty_most_common(self):
#         self.count()
#         self.number_counter = Counter(self.manual_count).most_common(20)
#         for bgr, value in self.number_counter:
#             print(bgr, value, ((float(value) / self.total_pixels) * 100))

#     def detect(self):
#         self.twenty_most_common()
#         self.percentage_of_first = float(self.number_counter[0][1]) / self.total_pixels
#         if self.percentage_of_first > 0.5:
#             return self.number_counter[0][0]
#         else:
#             return self.average_colour()

#     def contrast_color(self):
#         color = self.detect()
#         print("Detected color:", color)
#         r, g, b = color
#         luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
#         print("luminance: ", luminance)
#         return (0, 0, 0) if luminance > 0.028 else (255, 255, 255)
