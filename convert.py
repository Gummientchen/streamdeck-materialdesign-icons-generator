import os
import glob
from pathlib import Path
from multiprocessing import Pool
# from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps, ImageDraw
from tqdm import tqdm

## settings
pool_size = 16  # your "parallelness"
width = 144
height = 144
transitionDuration = 50 # in milliseconds
transitionFrames = 2 # inbetween frames for transition

## define your wanted color variations here

# name, (icon color), (background color), [animated versions [icon color, background color, name]]

variants = [
    ["aqua", (0, 200, 253), (11, 27, 56), [
        [False, (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [(255,255,255), (29, 89, 208), "bneubrakbay"]
    ]],
    ["blue", (59, 123, 255), (11, 27, 56), [
        [False, (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [(255,255,255), (29, 89, 208), "bneubrakbay"]
    ]],
    ["green", (47, 199, 134), (11, 27, 56), [
        [False, (217, 53, 38), "shojohired"],
        [(255,255,255), (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["orange", (255, 109, 76), (11, 27, 56), [
        [(255,255,255), (217, 53, 38), "shojohired"],
        [(255,255,255), (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["pink", (194, 89, 240), (11, 27, 56), [
        [(255,255,255), (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["pink2", (235, 82, 148), (11, 27, 56), [
        [(255,255,255), (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["yellow", (247, 206, 0), (11, 27, 56), [
        [False, (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["red", (247, 0, 0), (11, 27, 56), [
        [(255,255,255), (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]],
    ["white", (252, 252, 252), (11, 27, 56), [
        [False, (217, 53, 38), "shojohired"],
        [False, (0, 180, 120), "greenteal"],
        [False, (29, 89, 208), "bneubrakbay"]
    ]]
]

## settings
pool_size = 16  # your "parallelness"
width = 144
height = 144
transitionDuration = 50 # in milliseconds
transitionFrames = 2 # inbetween frames for transition

# create directories
if not os.path.exists("input"):
    os.makedirs("input")
if not os.path.exists("output"):
    os.makedirs("output")
if not os.path.exists("tmp"):
    os.makedirs("tmp")

# get all svg files from input
items = glob.glob("input/*.svg")

def blendColors(color1, color2, step, steps):
    r1 = color1[0]
    g1 = color1[1]
    b1 = color1[2]

    r2 = color2[0]
    g2 = color2[1]
    b2 = color2[2]

    diffR = r2 - r1
    diffG = g2 - g1
    diffB = b2 - b1

    r0 = r1 + (diffR * step / steps)
    g0 = g1 + (diffG * step / steps)
    b0 = b1 + (diffB * step / steps)

    color = (int(r0), int(g0), int(b0))

    return color

def frameTimes(steps, transitionTime = 60):
    intFrames = steps - 1

    transitionFrame = int(transitionTime / intFrames)

    normalFrame = int((1000 - transitionTime*2)/2)

    frameTimes = []
    frameTimes.append(normalFrame)

    for f in range(steps-1):
        frameTimes.append(transitionFrame)
    
    frameTimes.append(normalFrame)

    for f in range(steps-1):
        frameTimes.append(transitionFrame)

    return frameTimes


def interpolate(f_co, t_co, interval):
    det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]

# created the final icon
def createIcon(icon, color, backgroundColor = (11, 27, 56), convert=True):
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
    
    if(convert == True):
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
    
    try:
        iconCombined = Image.alpha_composite(iconBackground, icon)
    except ValueError as ve:
        # silently ignore broken images
        return
    
    iconRGB = iconCombined.convert("RGB")
    iconInverted = ImageOps.invert(iconRGB).convert("L")

    # Color variants
    for variant in variants:
        iconVariant = createIcon(iconInverted, variant[1], variant[2])
        outputFilename = "".join([outputFolder, "/", filename, "-",variant[0],".png"])
        iconVariant.save(outputFilename, optimize = True)
        
        # TODO: Make all color variants change from original color to white icon

        steps = transitionFrames + 1

        for idx, aniVariant in enumerate(variant[3]):
            if(aniVariant[0] == False):
                iconColor = variant[1]
            else:
                iconColor = aniVariant[0]


            frames = []
            for step in range(steps+1):
                if(aniVariant == False):
                    frames.append(createIcon(iconInverted, iconColor, blendColors(variant[2], aniVariant[1], step, steps), False))
                else:
                    frames.append(createIcon(iconInverted, blendColors(variant[1], iconColor, step, steps), blendColors(variant[2], aniVariant[1], step, steps), False))
            
            framesInverted = frames[::-1]
            framesInverted.pop()
            frames.pop()

            frames = framesInverted + frames

            outputFolderAnimated = "".join([outputFolder, "/animated_",aniVariant[2],"/"])

            # create output folder
            if not os.path.exists(outputFolderAnimated):
                os.makedirs(outputFolderAnimated)
            
            outputFilename = "".join([outputFolderAnimated, filename, "-",variant[0],"_bg",aniVariant[2],"_animated.gif"])

            frameOne = frames[0]

            duration = frameTimes(steps, transitionDuration)
            
            frameOne.save(outputFilename, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True)
        

if __name__ == "__main__":
    # create directories
    print("Creating Output Directories...")
    if not os.path.exists("input"):
        os.makedirs("input")
    if not os.path.exists("output"):
        os.makedirs("output")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    print("Getting All Icons...")
    # get all svg files from input
    items = glob.glob("input/*.svg")
    
    print("Generating Icons...")
    
    #multithreading
    numberOfItems = len(items)
    
    with Pool(processes=pool_size) as p, tqdm(total=numberOfItems) as pbar:
        for item in p.imap_unordered(createPNGfromSVG, items):
            pbar.update()
            pbar.refresh()