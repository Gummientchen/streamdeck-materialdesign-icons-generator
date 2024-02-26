import os
import glob
from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps


## define your wanted color variations here
variants = [
    ["aqua", (0, 200, 253), (11, 27, 56)],
    ["blue", (59, 123, 255), (11, 27, 56)],
    ["green", (47, 199, 134), (11, 27, 56)],
    ["orange", (255, 109, 76), (11, 27, 56)],
    ["pink", (194, 89, 240), (11, 27, 56)],
    ["pink2", (235, 82, 148), (11, 27, 56)],
    ["yellow", (247, 206, 0), (11, 27, 56)],
    ["red", (247, 0, 0), (11, 27, 56)]
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

# created the final icon
def createIcon(icon, color, backgroundColor = (11, 27, 56)):
    # Foreground
    foreground  = Image.new( mode = "RGB", size = (96, 96), color = color )
    foreground.putalpha(icon)

    # Background
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