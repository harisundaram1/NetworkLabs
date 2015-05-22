from PIL import Image, ImageDraw, ImageFont, ImageFilter
from random import randint
from scipy import ndimage
import numpy 

hex_black = '%02x%02x%02x' % (0,0,0)
hex_black = int(hex_black, 16)

hex_white = '%02x%02x%02x' % (255,255,255)
hex_white = int(hex_white, 16)

# overlays text on an image
def draw_text(text, color, font_size, base, coordinates):
	# make a blank image for the text, initialized to transparent text color
	txt = Image.new('RGBA', base.size, (255,255,255,0))

	# get a font
	fnt = ImageFont.truetype('/System/Library/Fonts/Helvetica.dfont', font_size)
	# get a drawing context
	d = ImageDraw.Draw(txt)

	d.text(coordinates, text, font=fnt, fill=color+(255,))
	
	out = Image.alpha_composite(base, txt)

	return out

# returns the width and height in pixels of the text
def text_size(text, font_size):
	# make a blank image for the text, initialized to transparent text color
	txt = Image.new('RGBA', (font_size*len(text), font_size*len(text)) , (255,255,255,0))

	# get a font
	fnt = ImageFont.truetype('/System/Library/Fonts/Helvetica.dfont', font_size)

	# get a drawing context
	d = ImageDraw.Draw(txt)

	d.text((0,0), text, font=fnt, fill=(0,0,0,255))

	text_size = (d.textsize(text, fnt))

	return text_size

def overlay_whole_begin(text,filename):
	#text = "20% of your friends eat at chipotle"
	font_size = 200
	random_num = randint(1,20)
	img_file = '/Local/Users/dev/NetworkLabs/topgenerator/data/img/food/'+str(random_num)+'.jpg'
	base = Image.open(img_file).convert('RGBA')
	base_w, base_h = base.size

	# remove 10 border
	base_w = base_w - 20
	base_h = base_h - 20

	# overlay dark canvas
	canvas = Image.new("RGBA", base.size, (0,0,0,128))
	combined = Image.alpha_composite(base, canvas)

	original = combined

	words = text.split(' ')
	words = [word+' ' for word in words]
	
	# find text size and store in list
	size_list = []	# list of word sizes
	for word in words:
		text_dim = text_size(word, font_size)
		size_list.append(text_dim)

	done = False
	new_size_list = []

	while not done:
		has_new_font_size = False

		x = 10
		y = 10

		for i in range(len(size_list)):
			print(words[i])

			w = size_list[i][0]
			h = size_list[i][1] 

			# if word is longer than image width, decrease font size
			# until word can fit in width and reset the process
			while(w > base_w):
				print("word too long ", w, base_w)
				font_size = font_size - 1
				has_new_font_size = True

				new_size_list = []
				for word in words:
					text_dim = text_size(word, font_size)
					new_size_list.append(text_dim)
			
				size_list = new_size_list
				combined = original
				break

			# checks if current word fits in this row
			if x+w > base_w-10:
				# exceeds row width, go to next row by incrementing y by the height of the previous word
				print("exceeds row width")
				print(x, y, w, h)

				y = y+size_list[i-1][1]
				x = 10

				# draw text
				combined = draw_text(words[i], (256,256,256), font_size, combined, (x, y))
				x = x+w

				# check whether the current word overflows the height of the image
				# if it does, decrease font size by 1 and try again
				if(y+h > base_h-10):
					print("height exceeds")
					font_size = font_size - 1
					has_new_font_size = True

					new_size_list = []
					for word in words:
						text_dim = text_size(word, font_size)
						new_size_list.append(text_dim)
					size_list = new_size_list
					combined = original
					break

			else:
				# word does not exceed current row width
				print("does not exceed. x = ", x)
				combined = draw_text(words[i], (256,256,256), font_size, combined, (x, y))
				x = x+w

			if i==len(size_list)-1:
				done = True

	combined.save(filename)
	return

if __name__ == "__main__":
	overlay_whole_begin()
