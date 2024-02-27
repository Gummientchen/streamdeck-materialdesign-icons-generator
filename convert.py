import os
import glob
from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps, ImageDraw


## define your wanted color variations here
variants = [
    {"name": "aqua", "color": (0, 200, 253), "background": (11, 27, 56)},
    {"name": "blue", "color": (59, 123, 255), "background": (11, 27, 56)},
    {"name": "green", "color": (47, 199, 134), "background": (11, 27, 56)},
    {"name": "orange", "color": (255, 109, 76), "background": (11, 27, 56)},
    {"name": "pink", "color": (194, 89, 240), "background": (11, 27, 56)},
    {"name": "pink2", "color": (235, 82, 148), "background": (11, 27, 56)},
    {"name": "yellow", "color": (247, 206, 0), "background": (11, 27, 56)},
    {"name": "red", "color": (247, 0, 0), "background": (11, 27, 56)},
    {"name": "white", "color": (252, 252, 252), "background": (11, 27, 56)},
    {"name": "nvidia", "color": (255,255,255), "background": [(123,185,7),(55,141,52)]},
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
    
    # Background animated
    animatedRed = Image.new( mode = "RGBA", size = (width, height), color = (200,0,0) )
    animatedGreen = Image.new( mode = "RGBA", size = (width, height), color = (0,220,0) )

    # composite icon
    background.paste(foreground, (24, 8), foreground)
    animatedRed.paste(foreground, (24, 8), foreground)
    animatedRed1 = Image.blend(background, animatedRed, 0.25)
    animatedRed2 = Image.blend(background, animatedRed, 0.5)
    animatedRed3 = Image.blend(background, animatedRed, 0.75)
    animatedGreen.paste(foreground, (24, 8), foreground)
    animatedGreen1 = Image.blend(background, animatedGreen, 0.25)
    animatedGreen2 = Image.blend(background, animatedGreen, 0.5)
    animatedGreen3 = Image.blend(background, animatedGreen, 0.75)
    

    # reduce colors
    background = background.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedRed = animatedRed.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedRed1 = animatedRed1.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedRed2 = animatedRed2.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedRed3 = animatedRed3.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedGreen = animatedGreen.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedGreen1 = animatedGreen1.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedGreen2 = animatedGreen2.convert("P", palette=Image.ADAPTIVE, colors=64)
    animatedGreen3 = animatedGreen3.convert("P", palette=Image.ADAPTIVE, colors=64)

    animatedRedIcon = [
        animatedRed,
        animatedRed1,
        animatedRed2,
        animatedRed3
    ]

    animatedGreenIcon = [
        animatedGreen,
        animatedGreen1,
        animatedGreen2,
        animatedGreen3
    ]

    return background, animatedRedIcon, animatedGreenIcon

# prepares the icon vor generation
def createPNGfromSVG(svgFilename):
    filename = os.path.basename(svgFilename)
    filename = os.path.splitext(filename)[0]
    tmpFilename = "".join(["tmp/", filename, ".png"])
    outputFolder = "".join(["output/", filename])
    outputFolderAnimatedRed = "".join(["output/", filename, "/animated-red"])
    outputFolderAnimatedGreen = "".join(["output/", filename, "/animated-green"])

    # create output folder
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    if not os.path.exists(outputFolderAnimatedRed):
        os.makedirs(outputFolderAnimatedRed)
    if not os.path.exists(outputFolderAnimatedGreen):
        os.makedirs(outputFolderAnimatedGreen)

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
        iconVariant, iconVariantAnimatedRed, iconVariantAnimatedGreen = createIcon(iconInverted, variant["color"], variant["background"])

        outputFilename = "".join([outputFolder, "/", filename, "-",variant["name"],".png"])
        outputFilenameAnimatedRed = "".join([outputFolderAnimatedRed, "/", filename, "-",variant["name"],"-animated-red.gif"])
        outputFilenameAnimatedGreen = "".join([outputFolderAnimatedGreen, "/", filename, "-",variant["name"],"-animated-green.gif"])

        iconVariant.save(outputFilename, optimize = True)
        iconVariant.save(
            outputFilenameAnimatedRed,
            optimize = False,
            save_all=True,
            append_images=[
                iconVariant,
                iconVariant,
                iconVariant,
                iconVariantAnimatedRed[1],
                iconVariantAnimatedRed[2],
                iconVariantAnimatedRed[3],
                iconVariantAnimatedRed[0]
                ],
            duration=125,
            loop=0)
        iconVariant.save(
            outputFilenameAnimatedGreen,
            optimize = False,
            save_all=True,
            append_images=[
                iconVariant,
                iconVariant,
                iconVariant,
                iconVariantAnimatedGreen[1],
                iconVariantAnimatedGreen[2],
                iconVariantAnimatedGreen[3],
                iconVariantAnimatedGreen[0]
                ],
            duration=125,
            loop=0)

#multithreading
pool = Pool(pool_size)
for item in items:
    pool.apply_async(createPNGfromSVG, (item,))

pool.close()
pool.join()