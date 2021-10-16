from PIL import Image, ImageColor, ImageDraw, ImageFont
from base64 import encodebytes
from flask import jsonify
from io import BytesIO
import random

class Captcha:
    def __init__(self, char_count, decoy_count, char_color, decoy_color, noise_color='#b5d439', filter=False, filter_chars = []):
        self.width = 300
        self.height = 100
        self.char_count = char_count or 5
        self.decoy_count = decoy_count or 4
        self.char_color = ImageColor.getrgb(char_color or "#03fc3d")
        self.decoy_color = ImageColor.getrgb(decoy_color or "#757373")
        self.noise_color = ImageColor.getrgb(noise_color or "#b5d439")
        self.chars = self.get_chars(filter or False, filter_chars or [])

    def generate(self):
        image = Image.new("RGBA", (self.width, self.height), color=0)
        font = ImageFont.truetype("assets/NotoSansMono.ttf", 40)
        decoy_font = ImageFont.truetype("assets/open-sans.light.ttf", 35)
        draw = ImageDraw.Draw(image, "RGBA")

        decoy_start_x = 25
        decoy_segment = int(300 / self.decoy_count)
        for i in range(1, self.decoy_count+1):
            index = random.randint(0, len(self.chars)-1)
            cur_char = self.chars[index] # character selected
            # for uniform distribution of decoy instead of all of them sticking at single place
            # reducing 20 from width because of font size
            pos_decoy_x = random.randint(decoy_start_x - 10, self.width - 20 if decoy_segment * i > self.width - 20 else decoy_segment * i)
            # goto next segment
            decoy_start_x += decoy_segment
            # height from top for decoy character (reducing 40 bc of font size)
            pos_decoy_y = random.randint(5, self.height - 40)
            draw.text((pos_decoy_x, pos_decoy_y), cur_char, self.decoy_color, font=decoy_font)

        # segmenting for each actual characters
        segment = int(self.width/self.char_count) - 10
        drawn_chars = []
        noise_coordinates = []
        x_starting = 10
        for i in range(1, self.char_count+1):
            index = random.randint(0, len(self.chars)-1)
            # character selection
            cur_char = self.chars[index]
            # chararcters to be sent for validation
            drawn_chars.append(cur_char)
            # position for character in each segment
            pos_x = random.randint(x_starting, segment * i)
            # incrementing to next segment
            x_starting += segment + 5
            # height from top for character (-50 bc of font)
            pos_y = random.randint(10, self.height - 50)
            draw.text((pos_x, pos_y), cur_char, self.char_color, font=font)
            # this is to ensure that almost every character get noise lines
            noise_coordinates.append((pos_x+10, pos_y+25))

        #draw the noise lines    
        draw.line(noise_coordinates, fill=self.noise_color, width=2)

        #image.save('test.png')

        json = self.convert(image, drawn_chars)
        return json


    def get_chars(self, filter, filter_chars):
        ALL_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        if not filter: 
            return ALL_CHARS
        
        chars = list(ALL_CHARS)
        for char in filter_chars:
            chars.remove(char)
        return ''.join(chars)

    def convert(self, image, char):
        b = BytesIO()
        image.save(b, format='png')
        b.seek(0)
        # encode to base64
        encoded_img = encodebytes(b.getvalue()).decode('ascii')
        return jsonify(data=encoded_img, text=''.join(char))