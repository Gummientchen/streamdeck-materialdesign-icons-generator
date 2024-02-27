import os
import glob
import math
import time

from tqdm import tqdm

from multiprocessing.pool import ThreadPool as Pool
os.environ['path'] += r';C:\Program Files\Inkscape\bin'

from cairosvg import svg2png
from PIL import Image, ImageOps, ImageDraw

start_time = time.time()

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

final_size = 72, 72

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

# create animated frames
def createAnimatedIcon(name, foreground, background, duration = 1000, backgroundColor = (200,0,0), frames = 4):
    icon = Image.new( mode = "RGBA", size = (width, height), color = backgroundColor )
    icon.paste(foreground, (24, 8), foreground)

    animatedframes = []


    for f in range(frames):
        frame = Image.blend(background, icon, 1/frames*(f+1))
        frame.thumbnail(final_size, Image.Resampling.LANCZOS)
        frame = frame.convert("P", palette=Image.ADAPTIVE, colors=64)
        animatedframes.append(frame)
    
    animation = {
        "name": name,
        "duration": duration,
        "frames": animatedframes
    }

    return animation


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
    
    # composite icon
    background.paste(foreground, (24, 8), foreground)
    
    # define animated versions here
    animations = []
    animations.append(createAnimatedIcon("red", foreground, background, 1000, (200,0,0), 8))
    animations.append(createAnimatedIcon("green", foreground, background, 1000, (0,220,0), 8))
    animations.append(createAnimatedIcon("orange", foreground, background, 1000, (255, 109, 76), 8))
    
    # scale down and reduce colors
    background.thumbnail(final_size, Image.Resampling.LANCZOS)
    background = background.convert("P", palette=Image.ADAPTIVE, colors=64)

    return background, animations

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
    try:
        icon = Image.open(tmpFilename)
        iconBackground  = Image.new( mode = "RGBA", size = (96, 96), color = (255, 255, 255) )
        iconCombined = Image.alpha_composite(iconBackground, icon)
        iconRGB = iconCombined.convert("RGB")
        iconInverted = ImageOps.invert(iconRGB).convert("L")
    except ValueError:
        print("images do not match:", svgFilename)
        return False

    # Color variants
    for variant in variants:
        outputFilename = "".join([outputFolder, "/", filename, "-",variant["name"],".png"])

        if not os.path.isfile(outputFilename):
            iconVariant, animations = createIcon(iconInverted, variant["color"], variant["background"])
            iconVariant.save(outputFilename, optimize = True)

            for animation in animations:
                outputFolderAnimated = "".join(["output/", filename, "/animated-", animation["name"]])
                if not os.path.exists(outputFolderAnimated):
                    os.makedirs(outputFolderAnimated)
                outputFilenameAnimated = "".join([outputFolderAnimated, "/", filename, "-",variant["name"],"-animated-",animation["name"],".gif"])
                
                images = []

                for frame in animation["frames"]:
                    images.append(frame)

                for img in range(len(animation["frames"])-1):
                    images.append(iconVariant)

                duration = math.floor(animation["duration"] / (len(animation["frames"])*2))


                iconVariant.save(
                    outputFilenameAnimated,
                    optimize = True,
                    save_all=True,
                    append_images=images,
                    duration=duration,
                    loop=0)

def main():
    #multithreading
    # pool = Pool(pool_size)

    # for item in items:
    #     pool.apply_async(createPNGfromSVG, (item,))

    for item in tqdm(items):
        createPNGfromSVG(item)

    # pool.close()
    # pool.join()

if __name__ == "__main__":
    main()

print("--- %s seconds ---" % (time.time() - start_time))