import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import requests
import hashlib

name = b"Preslav Aleksandrov"

# major grid division
grid_w = 5
grid_h = 5

# minor grid division
subGrid_w = 1
subGrid_h = 1

# up to 8 probabilityes
available_shapes = np.zeros(8) 

# genertae pattern matrix
matrix = np.zeros((grid_w, grid_h, subGrid_w, subGrid_h))

# image properties
w = 1000
h = 1000
block_w = w//grid_w
block_h = h//grid_h
subBlocl_w = block_w//subGrid_w
subBlocl_h = block_h//subGrid_h

# final image plus border
w_g = 1200
h_g = 1200

# image colors
background_color = "#FCFAFF"
foreground_color = "#4169e1"

# generate true random numbers
URL = "http://www.random.org/integers/?num=100&min=0&max=10000&col=1&base=10&format=plain&rnd=new"
rand = np.fromstring(requests.get(url = URL).text, sep="\n")/10000


# turn seed string into Monte-Carlo probabilites
m = hashlib.sha256()
m.update(name)
probs = np.array([int(m.hexdigest()[i:i+4], 16) for i in range(0, len(m.hexdigest()), 4)])
probs = np.cumsum(probs/np.sum(probs))

# populate pattern matrix with shapes based on MC
with np.nditer(matrix, flags=['c_index'], op_flags=['writeonly']) as it:
    for x in it:
        x[...] = np.argmax(probs>=rand[it.index])


# Image generation
image = Image.new('RGB', (w, h))
background = Image.new('RGB', (w_g,h_g))

draw_background = ImageDraw.Draw(background)
draw_background.rectangle(xy=(0,0,w_g,h_g), fill=background_color)

draw = ImageDraw.Draw(image)
draw.rectangle(xy=(0,0,w,h), fill=background_color)

# for each pattern draw an image in the correct spot
with np.nditer(matrix, flags=['multi_index'], op_flags=['readonly']) as it:
    for item in it:
        x_f = it.multi_index[0]*block_w+it.multi_index[2]*subBlocl_w
        y_f = it.multi_index[1]*block_h+it.multi_index[3]*subBlocl_h
        x_s = x_f+subBlocl_w
        y_s = y_f+subBlocl_h
        x_c = (x_f+x_s)/2
        y_c = (y_f+y_s)/2
        r = min(subBlocl_w,subBlocl_h)/2
        # select what to draw, process under 4 is square, process 4 is a circle and process above 4 is empty
        if item < 6:
            draw.rectangle(xy=(x_f,y_f,x_s,y_s), fill=foreground_color)
        if item == 6:
            draw.ellipse(xy=(x_f,y_f,x_s,y_s), fill=foreground_color)
        # if item == 4:
        #     draw.regular_polygon((x_c,y_c, r),n_sides=3 ,rotation=0, fill='orange')
            
            
# save image
background.paste(image, ((w_g-w)//2,(h_g-h)//2))
background.filter(ImageFilter.SMOOTH)
background.save("img.png")


