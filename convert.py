import os
import glob
from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps

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

def createIcon(icon, color):
    # Foreground
    foreground  = Image.new( mode = "RGB", size = (96, 96), color = color )
    foreground.putalpha(icon)

    # Background
    background  = Image.new( mode = "RGBA", size = (width, height), color = (11, 27, 56) )
    background.paste(foreground, (24, 8), foreground)

    background = background.convert("P", palette=Image.ADAPTIVE, colors=64)

    return background

def createPNGfromSVG(svgFilename):
    filename = os.path.basename(svgFilename)
    filename = os.path.splitext(filename)[0]
    tmpFilename = "".join(["tmp/", filename, ".png"])
    outputFolder = "".join(["output/", filename])

    # create output folder
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    # Output Filenames for color variants
    outputFilenameAqua = "".join([outputFolder, "/", filename, "-aqua.png"])
    outputFilenameBlue = "".join([outputFolder, "/", filename, "-blue.png"])
    outputFilenameGreen = "".join([outputFolder, "/", filename, "-green.png"])
    outputFilenameOrange = "".join([outputFolder, "/", filename, "-orange.png"])
    outputFilenamePink = "".join([outputFolder, "/", filename, "-pink.png"])
    outputFilenamePink2 = "".join([outputFolder, "/", filename, "-pink2.png"])

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
    iconAqua = createIcon(iconInverted, (0, 200, 253))
    iconAqua.save(outputFilenameAqua, optimize = True)

    iconBlue = createIcon(iconInverted, (59, 123, 255))
    iconBlue.save(outputFilenameBlue, optimize = True)

    iconGreen = createIcon(iconInverted, (47, 199, 134))
    iconGreen.save(outputFilenameGreen, optimize = True)

    iconOrange = createIcon(iconInverted, (255, 109, 76))
    iconOrange.save(outputFilenameOrange, optimize = True)

    iconPink = createIcon(iconInverted, (194, 89, 240))
    iconPink.save(outputFilenamePink, optimize = True)

    iconPink2 = createIcon(iconInverted, (235, 82, 148))
    iconPink2.save(outputFilenamePink2, optimize = True)


pool = Pool(pool_size)
for item in items:
    pool.apply_async(createPNGfromSVG, (item,))

pool.close()
pool.join()