import os
import glob
from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps, ImageDraw


## define your wanted color variations here
variants = [
    ["aqua", (0, 200, 253), (11, 27, 56)],
    ["blue", (59, 123, 255), (11, 27, 56)],
    ["green", (47, 199, 134), (11, 27, 56)],
    ["orange", (255, 109, 76), (11, 27, 56)],
    ["pink", (194, 89, 240), (11, 27, 56)],
    ["pink2", (235, 82, 148), (11, 27, 56)],
    ["yellow", (247, 206, 0), (11, 27, 56)],
    ["red", (247, 0, 0), (11, 27, 56)],
    ["white", (252, 252, 252), (11, 27, 56)],
    ["nvidia", (255,255,255), [
        (123,185,7),
        (55,141,52)
    ]]
]

## settings
pool_size = 16  # your "parallelness"
width = 144
height = 144

# create directories
if not os.path.exists("input"):
    os.makedirs("input")
if not os.path.exists("output"):
    os.makedirs("output")
if not os.path.exists("tmp"):
    os.makedirs("tmp")

# get all svg files from input
items = glob.glob("input/*.svg")

def interpolate(f_co, t_co, interval):
    det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]

# created the final icon
def createIcon(icon, color, backgroundColor = (11, 27, 56)):
    # Foreground
    foreground  = Image.new( mode = "RGB", size = (96, 96), color = color )
    foreground.putalpha(icon)

    # Background
    if type(backgroundColor) == list:
        background  = Image.new( mode = "RGBA", size = (width, height), color = 0 )
        draw = ImageDraw.Draw(background)
        for i, color in enumerate(interpolate(backgroundColor[0], backgroundColor[1], background.width * 2)):
            draw.line([(0, i), (background.width, i)], tuple(color), width=1)
    else:
        background  = Image.new( mode = "RGBA", size = (width, height), color = backgroundColor )

    background.paste(foreground, (24, 8), foreground)
    background = background.convert("P", palette=Image.ADAPTIVE, colors=64)

    return background

# prepares the icon vor generation
def createPNGfromSVG(svgFilename):
    filename = os.path.basename(svgFilename)
    filename = os.path.splitext(filename)[0]
    tmpFilename = "".join(["tmp/", filename, ".png"])
    outputFolder = "".join(["output/", filename])

    # create output folder
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    # convert SVG to PNG if neccessary
    if not os.path.isfile(tmpFilename):
        svg2png(
            url=svgFilename, scale=4, write_to=tmpFilename)
    
    # Icon
    icon = Image.open(tmpFilename)
    iconBackground  = Image.new( mode = "RGBA", size = (96, 96), color = (255, 255, 255) )
    iconCombined = Image.alpha_composite(iconBackground, icon)
    iconRGB = iconCombined.convert("RGB")
    iconInverted = ImageOps.invert(iconRGB).convert("L")

    # Color variants
    for variant in variants:
        iconVariant = createIcon(iconInverted, variant[1], variant[2])
        outputFilename = "".join([outputFolder, "/", filename, "-",variant[0],".png"])
        iconVariant.save(outputFilename, optimize = True)

#multithreading
pool = Pool(pool_size)
for item in items:
    pool.apply_async(createPNGfromSVG, (item,))

pool.close()
pool.join()