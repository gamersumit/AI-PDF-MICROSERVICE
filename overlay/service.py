import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from utils import Mail, MediaUtils, PDFUtils
from collections import Counter


class PDFService:
    @staticmethod
    def generate_pdf(illustrations, title):
        image = illustrations[0]
        image = MediaUtils.download_image(image_url= image['overlay_image_url'])
        
        pdf = PDFUtils(title = title, width=image.width, height=image.height)
        pdf.add_title_page()
        
        for illustration in illustrations :
            image = MediaUtils.download_image(image_url= illustration['overlay_image_url'])
            pdf.append_images_to_pdf([image])
        
        pdf = pdf.save()
        return MediaUtils.UploadMediaToCloud(pdf, 'pdf', title.strip())
    
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


class FontColorForBackgroundDetectorService:
    def __init__(self, image):
        self.img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)  # Convert PIL image to NumPy array
        self.manual_count = {}
        self.h, self.w, self.channels = self.img.shape
        self.total_pixels = self.h * self.w

    def count(self):
        for y in range(0, self.h):
            for x in range(0, self.w):
                BGR = (self.img[y, x, 0], self.img[y, x, 1], self.img[y, x, 2])
                if BGR in self.manual_count:
                    self.manual_count[BGR] += 1
                else:
                    self.manual_count[BGR] = 1

    def average_colour(self):
        red, green, blue = 0, 0, 0
        sample = 10
        for top in range(0, sample):
            blue += self.number_counter[top][0][0]
            green += self.number_counter[top][0][1]
            red += self.number_counter[top][0][2]

        average_red = red / sample
        average_green = green / sample
        average_blue = blue / sample
        print("Average RGB for top ten is: (", average_red, ", ", average_green, ", ", average_blue, ")")
        
        return (average_red, average_green, average_blue)

    def twenty_most_common(self):
        self.count()
        self.number_counter = Counter(self.manual_count).most_common(20)
        for bgr, value in self.number_counter:
            print(bgr, value, ((float(value) / self.total_pixels) * 100))

    def detect(self):
        self.twenty_most_common()
        self.percentage_of_first = float(self.number_counter[0][1]) / self.total_pixels
        if self.percentage_of_first > 0.5:
            return self.number_counter[0][0]
        else:
            return self.average_colour()

    def contrast_color(self):
        color = self.detect()
        print("Detected color:", color)
        r, g, b = color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        print("luminance: ", luminance)
        return (0, 0, 0) if luminance > 0.028 else (255, 255, 255)

# class TextOverlay():       
#     def wrap_text(self, draw, text, font, max_width):
#         print("in wrap text")
#         lines = []
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
#         return lines
        
#     def text_overlay(self, illustrations):        
#         counter = 0
#         print("in text overlay")
        
#         for illustration in illustrations:
#             print("illustration: ", illustration)
#             image_id = illustration['id']
#             print("image id: ", image_id)
#             image_url = illustration['image_url']
#             print("image_urlL :", image_url)
#             text_to_be_overlayed = illustration['text']
        
        
#             image = MediaUtils.download_image(image_url)

#             font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()

#             # font_color_detector = FontColorForBackgroundDetector(image_url).contrast_color()
#             print("font_color: ", font_color_detector)
#             fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
            
#             font_path = os.getenv('FONT_PATH')
#             font_size = 41
#             print("font size")
#             font = ImageFont.truetype(font_path, font_size)

#             draw = ImageDraw.Draw(image)
#             print("draw")
#             print("out wrap text")
#             # Set maximum width for wrapping
#             max_text_width = image.width - 30  
#             wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
#             print("wrapped")
#             # Calculate total height required for wrapped text
#             total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)

#             fixed_y = image.height - 135

#             # Calculate starting y position to center vertically
#             y = fixed_y - total_text_height // 2

#             # Draw wrapped text with center alignment
#             for line in wrapped_text_lines:
#                 # Calculate width and height of the line of text
#                 text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]

#                 # Calculate starting x position to center align the line horizontally
#                 x = (image.width - text_width) // 2

#                 # Draw the line of text
#                 draw.text((x, y), line, fill=fill, font=font)

#                 # Move to the next line vertically
#                 y += text_height

#             print("done hai uye to")
            
#             # Save the image to a BytesIO object
#             image_bytes = BytesIO()
#             image.save(image_bytes, format='JPEG')
#             image_bytes.seek(0)
            

#             # Save the image to Cloudinary
#             image_name = f"{image_id}_page{counter}_text"
#             saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
#             print("img url: ", saved_img_url)
#             illustration['overlay_image_url'] = saved_img_url
        
#         return illustrations

class BackgroundBox:
    @staticmethod
    def textWithBackground(img, text, font, fontScale, textPos, textThickness=1, textColor=(0, 255, 0), bgColor=(0, 0, 0), pad_x=3, pad_y=3, bgOpacity=0.5):
        (t_w, t_h), _ = cv2.getTextSize(text, font, fontScale, textThickness) # getting the text size
        x, y = textPos
        overlay = img.copy() # copying the image
        cv2.rectangle(overlay, (x - pad_x, y + pad_y), (x + t_w + pad_x, y - t_h - pad_y), bgColor, -1) # draw rectangle
        new_img = cv2.addWeighted(overlay, bgOpacity, img, 1 - bgOpacity, 0) # overlaying the rectangle on the image.
        cv2.putText(new_img, text, textPos, font, fontScale, textColor, textThickness) # draw in text
        return new_img

class TextOverlay:
    def download_image(self, image_url):
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image

    def wrap_text(self, draw, text, font, max_width):
        print("in wrap text")
        lines = []
        words = text.split()
        print("words: ", words)
        
        while words:
            line = ""
            while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                line += words.pop(0) + " "
            
            # If there are no words left, add the current line and break
            if not words:
                lines.append(line.strip())
                break
            
            # Check if the current word is too long to fit in an empty line
            word = words.pop(0)
            if draw.textbbox((0, 0), word, font=font)[2] > max_width:
                # Hyphenate the word and add parts to lines
                while word:
                    for i in range(1, len(word) + 1):
                        if draw.textbbox((0, 0), word[:i], font=font)[2] > max_width:
                            lines.append(word[:i-1] + '-')
                            word = word[i-1:]
                            break
                    else:
                        lines.append(word)
                        word = ""
            else:
                lines.append(line.strip())
                lines.append(word)  
        return lines
        
    def text_overlay(self, illustrations):        
        counter = 0
        print("in text overlay")
        
        for illustration in illustrations:
            print("illustration: ", illustration)
            image_id = illustration['id']
            print("image id: ", image_id)
            image_url = illustration['image_url']
            print("image_urlL :", image_url)
            text_to_be_overlayed = illustration['text']
        
            image = self.download_image(image_url)

            font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()

            print("font_color: ", font_color_detector)
            fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
            
            font_path = os.getenv('FONT_PATH')
            font_size = 41
            print("font size")
            font = ImageFont.truetype(font_path, font_size)

            draw = ImageDraw.Draw(image)
            print("draw")
            print("out wrap text")
            max_text_width = image.width - 30  
            wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
            print("wrapped")
            total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)
            max_text_line_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in wrapped_text_lines)

            fixed_y = image.height - 135
            y = fixed_y - total_text_height // 2
            
            # Create OpenCV image for adding text with background
            img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            overlay = img_cv2.copy()

            # Draw a single background rectangle for all wrapped text lines
            rect_x1 = (image.width - max_text_line_width) // 2 - 10
            rect_y1 = y - 10
            rect_x2 = (image.width + max_text_line_width) // 2 + 10
            rect_y2 = y + total_text_height + 10

            cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1) # Black background
            img_cv2 = cv2.addWeighted(overlay, 0.5, img_cv2, 0.5, 0) # Adjust the opacity
            
            # Draw wrapped text
            for line in wrapped_text_lines:
                text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
                x = (image.width - text_width) // 2
                img_cv2 = BackgroundBox.textWithBackground(img_cv2, line, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (x, y), textColor=(255, 255, 255), bgColor=(0, 0, 0), bgOpacity=0.5)
                y += text_height
            
            image = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
            
            image_bytes = BytesIO()
            image.save(image_bytes, format='JPEG')
            image_bytes.seek(0)

            image_name = f"{image_id}_page{counter}_text"
            saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
            illustration['overlay_image_url'] = saved_img_url

        return illustrations

# class BackgroundBox:    
#     def textWithBackground(img, text, font, fontScale, textPos, textThickness=1,textColor=(0,255,0), bgColor=(0,0,0), pad_x=3, pad_y=3, bgOpacity=0.5):
#         print("in textWithBackground")
#         (t_w, t_h), _= cv2.getTextSize(text, font, fontScale, textThickness) # getting the text size   
#         x, y = textPos        
#         print("one")
#         overlay = img.copy() # coping the image
#         print("two")
#         cv2.rectangle(overlay, (x-pad_x, y+ pad_y), (x+t_w+pad_x, y-t_h-pad_y), bgColor,-1) # draw rectangle 
#         print("three")
#         new_img = cv2.addWeighted(overlay, bgOpacity, img, 1 - bgOpacity, 0) # overlaying the rectangle on the image.
#         print("four")
#         cv2.putText(new_img,text, textPos,font, fontScale, textColor,textThickness ) # draw in text
#         print("five")
#         img = new_img
#         return img
    
# class TextOverlay:       
#     def download_image(self, image_url):
#         print("in download img", image_url)
#         response = requests.get(image_url)
#         image = Image.open(BytesIO(response.content))
#         print("type of image", type(image))
#         print("image ===>", image)
#         return image
    
#     def wrap_text(self, draw, text, font, max_width):
#         print("in wrap text")
#         lines = []
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
#         return lines
        
#     def text_overlay(self, illustrations):        
#         counter = 0
#         print("in text overlay")
        
#         for illustration in illustrations:
#             print("illustration: ", illustration)
#             image_id = illustration['id']
#             print("image id: ", image_id)
#             image_url = illustration['image_url']
#             print("image_urlL :", image_url)
#             text_to_be_overlayed = illustration['text']
        
        
#             image = self.download_image(image_url)
#             # background_textbox = BackgroundBox.textWithBackground(image_url)
#             font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()

#             print("font_color: ", font_color_detector)
#             fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
#             print("background textbos done, image is : ", image)
            
#             font_path = os.getenv('FONT_PATH')
#             font_size = 41
#             print("font size")
#             font = ImageFont.truetype(font_path, font_size)
#             image = BackgroundBox.textWithBackground(image, text_to_be_overlayed, font, 0.3, (image.width - 30, image.height - 30))

#             draw = ImageDraw.Draw(image)
#             print("draw")
#             print("out wrap text")
#             # Set maximum width for wrapping
#             max_text_width = image.width - 30  
#             wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
#             print("wrapped")
#             # Calculate total height required for wrapped text
#             total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)

#             fixed_y = image.height - 135

#             # Calculate starting y position to center vertically
#             y = fixed_y - total_text_height // 2

#             # Draw wrapped text with center alignment
#             for line in wrapped_text_lines:
#                 # Calculate width and height of the line of text
#                 text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]

#                 # Calculate starting x position to center align the line horizontally
#                 x = (image.width - text_width) // 2

#                 # Draw the line of text
#                 draw.text((x, y), line, fill=fill, font=font)

#                 # Move to the next line vertically
#                 y += text_height

#             print("done hai uye to")
            
#             # Save the image to a BytesIO object
#             image_bytes = BytesIO()
#             image.save(image_bytes, format='JPEG')
#             image_bytes.seek(0)
            

#             # Save the image to Cloudinary
#             image_name = f"{image_id}_page{counter}_text"
#             saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
#             illustration['overlay_image_url'] = saved_img_url
#             # illustration.save()
#             print("img url: ", saved_img_url)
        
#         return illustrations


# class BackgroundBox:
#     @staticmethod
#     def textWithBackground(img, text, font, fontScale, textPos, textThickness=1, textColor=(0, 255, 0), bgColor=(0, 0, 0), pad_x=3, pad_y=3, bgOpacity=0.5):
#         (t_w, t_h), _ = cv2.getTextSize(text, font, fontScale, textThickness) # getting the text size
#         x, y = textPos
#         overlay = img.copy() # copying the image
#         cv2.rectangle(overlay, (x - pad_x, y + pad_y), (x + t_w + pad_x, y - t_h - pad_y), bgColor, -1) # draw rectangle
#         new_img = cv2.addWeighted(overlay, bgOpacity, img, 1 - bgOpacity, 0) # overlaying the rectangle on the image.
#         cv2.putText(new_img, text, textPos, font, fontScale, textColor, textThickness) # draw in text
#         return new_img

# class TextOverlay:
#     def download_image(self, image_url):
#         response = requests.get(image_url)
#         image = Image.open(BytesIO(response.content))
#         return image

#     def wrap_text(self, draw, text, font, max_width):
#         lines = []
#         words = text.split()
        
#         while words:
#             line = ""
#             while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
#                 line += words.pop(0) + " "
            
#             if not words:
#                 lines.append(line.strip())
#                 break
            
#             word = words.pop(0)
#             if draw.textbbox((0, 0), word, font=font)[2] > max_width:
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
                
#         return lines

#     def text_overlay(self, illustrations):        
#         counter = 0
        
#         for illustration in illustrations:
#             image_id = illustration['id']
#             image_url = illustration['image_url']
#             text_to_be_overlayed = illustration['text']
        
#             image = self.download_image(image_url)
#             font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()
#             fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
            
#             font_path = os.getenv('FONT_PATH')
#             font_size = 41
#             font = ImageFont.truetype(font_path, font_size)

#             draw = ImageDraw.Draw(image)
            
#             max_text_width = image.width - 30
#             wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
#             total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)

#             fixed_y = image.height - 135
#             y = fixed_y - total_text_height // 2

#             for line in wrapped_text_lines:
#                 text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
#                 x = (image.width - text_width) // 2
                
#                 img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#                 img_cv2 = BackgroundBox.textWithBackground(img_cv2, line, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (x, y), textColor=(255, 255, 255), bgColor=(0, 0, 0), bgOpacity=0.5)
#                 image = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
#                 y += text_height

#             image_bytes = BytesIO()
#             image.save(image_bytes, format='JPEG')
#             image_bytes.seek(0)
            
#             image_name = f"{image_id}_page{counter}_text"
#             saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
#             illustration['overlay_image_url'] = saved_img_url
        
#         return illustrations


# class BackgroundBox:
#     @staticmethod
#     def textWithBackground(img, text, font, fontScale, textPos, textThickness=1, textColor=(0, 255, 0), bgColor=(0, 0, 0), pad_x=3, pad_y=3, bgOpacity=0.5):
#         (t_w, t_h), _ = cv2.getTextSize(text, font, fontScale, textThickness) # getting the text size
#         x, y = textPos
#         overlay = img.copy() # copying the image
#         cv2.rectangle(overlay, (x - pad_x, y + pad_y), (x + t_w + pad_x, y - t_h - pad_y), bgColor, -1) # draw rectangle
#         new_img = cv2.addWeighted(overlay, bgOpacity, img, 1 - bgOpacity, 0) # overlaying the rectangle on the image.
#         cv2.putText(new_img, text, textPos, font, fontScale, textColor, textThickness) # draw in text
#         return new_img

# class TextOverlay:
#     def download_image(self, image_url):
#         response = requests.get(image_url)
#         image = Image.open(BytesIO(response.content))
#         return image

#     def wrap_text(self, draw, text, font, max_width):
#         lines = []
#         words = text.split()
        
#         while words:
#             line = ""
#             while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
#                 line += words.pop(0) + " "
            
#             if not words:
#                 lines.append(line.strip())
#                 break
            
#             word = words.pop(0)
#             if draw.textbbox((0, 0), word, font=font)[2] > max_width:
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
                
#         return lines

#     def text_overlay(self, illustrations):        
#         counter = 0
        
#         for illustration in illustrations:
#             image_id = illustration['id']
#             image_url = illustration['image_url']
#             text_to_be_overlayed = illustration['text']
        
#             image = self.download_image(image_url)
#             font_color_detector = FontColorForBackgroundDetectorService(image).contrast_color()
#             fill = '#000000' if font_color_detector == (0, 0, 0) else '#FFFFFF'
            
#             font_path = os.getenv('FONT_PATH')
#             font_size = 41
#             font = ImageFont.truetype(font_path, font_size)

#             draw = ImageDraw.Draw(image)
            
#             max_text_width = image.width - 30
#             wrapped_text_lines = self.wrap_text(draw, text_to_be_overlayed, font, max_text_width)
            
#             # Calculate total width and height required for wrapped text
#             total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text_lines)
#             max_text_line_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in wrapped_text_lines)

#             fixed_y = image.height - 135
#             y = fixed_y - total_text_height // 2
            
#             # Position for the text box background
#             text_x = (image.width - max_text_line_width) // 2
#             text_y_top = y - 10
#             text_y_bottom = y + total_text_height + 10

#             # Create OpenCV image for adding text with background
#             img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#             # img_cv2 = BackgroundBox.textWithBackground(
#             #     img_cv2, 
#             #     "\n".join(wrapped_text_lines), 
#             #     cv2.FONT_HERSHEY_SIMPLEX, 
#             #     0.5, 
#             #     (text_x, fixed_y), 
#             #     textColor=(255, 255, 255), 
#             #     bgColor=(0, 0, 0), 
#             #     bgOpacity=0.5, 
#             #     pad_x=10, 
#             #     pad_y=10
#             # )
#             image = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))

#             image_bytes = BytesIO()
#             image.save(image_bytes, format='JPEG')
#             image_bytes.seek(0)
            
#             image_name = f"{image_id}_page{counter}_text"
#             saved_img_url = MediaUtils.UploadMediaToCloud(image_bytes, 'text_overlay', image_name)
#             illustration['overlay_image_url'] = saved_img_url
        
#         return illustrations
