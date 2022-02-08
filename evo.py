#!/usr/bin/python3
#
################################################################################################################################
#  name:  noah olmstead harvey
#  date:  04012022
#  idea:  this script evolves an image using another image as selection pressure
################################################################################################################################

####  IMPORTS  #################################################################################################################

import argparse
from PIL import Image
from random import gauss

####  FUNCTIONS  ###############################################################################################################

def resizeImages(img, env):
    width = min(img.width, env.width)                           #   get minimum width
    height = min(img.height, env.height)                        #   get minimum height

    imgCropped = img.crop((
        ((img.width - width) // 2),
        ((img.height - height) // 2),
        (((img.width - width) // 2) + width),
        (((img.height - height) // 2) + height)
        ))                                                      #   (left bound, upper bound, right bound, lower bound)

    envCropped = env.crop((
        ((env.width - width) // 2),
        ((env.height - height) // 2),
        (((env.width - width) // 2) + width),
        (((env.height - height) // 2) + height)
        ))
    
    return(imgCropped, envCropped)

def evolveImage(img, env, k="k9", m="std", s=0.1):
    newImg = Image.new("RGBA", (img.width, img.height), (0,0,0))

    for y in range(img.height):
        for x in range(img.width):
            newPixel = generatePixel(img, env, x, y, k, m, s)
            newImg.putpixel((x,y), newPixel)

    return(newImg)


def generatePixel(img, env, x, y, k, m, s):
    if(k == "k9"): adjacent = kernel9(img, x, y)
    elif(k == "k21"): adjacent = kernel21(img, x, y)
    elif(k == "k35"): adjacent = kernel35(img, x, y)
    else: adjacent = kernel9(img, x, y)
    return(generateValue(img, env, adjacent, m, s))


def generateValue(img, env, adjacent, m, s):
    if(m == "std"): return(stdGen(img, env, adjacent, s))
    else: return(stdGen(img, env, adjacent, s))


def kernel9(img, x, y):
    return([(kx,ky) for (kx,ky) in [
            ((x-1),(y-1)),(x,(y-1)),((x+1),(y-1)),
            ((x-1),y),(x,y),((x+1),y),
            ((x-1),(y+1)),(x,(y+1)),((x+1),(y+1))
        ] if((kx in range(img.width)) and (ky in range(img.height)))])


def kernel21(img, x, y):
    return([(kx,ky) for (kx,ky) in [
        ((x-1),(y-2)),(x,(y-2)),((x+1),(y-2)),
        ((x-2),(y-1)),((x-1),(y-1)),(x,(y-1)),((x+1),(y-1)),((x+2),(y-1)),
        ((x-2),y),((x-1),y),(x,y),((x+1),y),((x+2),y),
        ((x-2),(y+1)),((x-1),(y+1)),(x,(y+1)),((x+1),(y+1)),((x+2),(y+1)),
        ((x-1),(y+2)),(x,(y+2)),((x+1),(y+2))
    ] if((kx in range(img.width)) and (ky in range(img.height)))])


def kernel35(img, x, y):
    return([(kx,ky) for (kx,ky) in [
        ((x-1),(y-3)),(x,(y-3)),((x+1),(y-3)),
        ((x-2),(y-2)),((x-1),(y-2)),(x,(y-2)),((x+1),(y-2)),((x+2),(y-2)),
        ((x-3),(y-1)),((x-2),(y-1)),((x-1),(y-1)),(x,(y-1)),((x+1),(y-1)),((x+2),(y-1)),((x+3),(y-1)),
        ((x-3),y),((x-2),y),((x-1),y),(x,y),((x+1),y),((x+2),y),((x+3),y),
        ((x-3),(y+1)),((x-2),(y+1)),((x-1),(y+1)),(x,(y+1)),((x+1),(y+1)),((x+2),(y+1)),((x+3),(y+1)),
        ((x-2),(y+2)),((x-1),(y+2)),(x,(y+2)),((x+1),(y+2)),((x+2),(y+2)),
        ((x-1),(y+3)),(x,(y+3)),((x+1),(y+3))
    ] if((kx in range(img.width)) and (ky in range(img.height)))])


def inRange(n, r=256):                                          ##  ensures pixel values are in range and are ints
    if(n // r > 1): return(255)                                 #   changed
    elif(n // r < 0): return(0)
    else: return(int(n))                                        #   cast to int (floor)


def stdGen(img, env, adjacent, s):
    genitors = [img.getpixel(pixel)[:3] for pixel in adjacent]
    mutation = [(inRange(r * gauss(1, s)),inRange(g * gauss(1, s)),inRange(b * gauss(1, s))) for (r,g,b) in genitors]
    children = [((abs(mr - er) + abs(mg - eg) + abs(mb - eb)),mr,mg,mb) for (mr,mg,mb),(er,eg,eb) in 
               zip(mutation, [env.getpixel(pixel)[:3] for pixel in adjacent])]
    return(sorted(children)[0][1:])


####  MAIN  ####################################################################################################################


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fileIn",
        type=str,
        help="the filepath to the intput/start image"
    )
    parser.add_argument(
        "fileOut",
        type=str,
        help="the filepath to the output/end/target image"
    )
    parser.add_argument(
        "-k",
        "--kernel",
        type=str,
        choices=["k9", "k21", "k35"],
        default="k9",
        help="defines the size of the kernel (adjacent pixels checked)"
    )
    parser.add_argument(
        "-m",
        "--method",
        type=str,
        choices=["std"],
        default="std",
        help="defines the method used to select genitors/children"
    )
    parser.add_argument(
        "-s",
        "--sigma",
        type=float,
        default=0.1,
        help="defines the rate at which mutations effect the children"
    )
    parser.add_argument(
        "-g",
        "--generations",
        type=int,
        default=8,
        help="defines the number of generations to evolve the first image though"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        choices=["gif", "png"],
        default="gif",
        help="export the evolution as an animated gif, or as a series of images"
    )
    args = parser.parse_args()
    kernel, method, sigma, generations, out = args.kernel, args.method, args.sigma, args.generations, args.output

    image = Image.open(args.fileIn)                             #   convert all images to RGBA
    if(image.mode != "RGBA"): image.convert("RGBA")
    enviroment = Image.open(args.fileOut)
    if(enviroment.mode != "RGBA"): enviroment.convert("RGBA")

    if((image.width != enviroment.width) or (image.height != enviroment.height)):       #   crop images if needed
        print(f"Passed images not same size:  ({image.width}:{image.height}, {enviroment.width}:{enviroment.height})")
        image, enviroment = resizeImages(image, enviroment)

    if(out == "gif"):
        print(f"{1:0{3}}/{(generations+3):0{3}}: First Frame")
        frames = [evolveImage(image, image, kernel, method, sigma)]
        for i in range(generations):
            print(f"{(i+2):0{3}}/{(generations+3):0{3}}: Frame {(i+2):0{3}}")
            image = evolveImage(image, enviroment, kernel, method, sigma)               #   creates generation n image
            frames.append(image)
        print(f"{(generations+2):0{3}}/{(generations+3):0{3}}: Last Frame")
        frames.append(evolveImage(enviroment, enviroment, kernel, method, sigma))
        print(f"{(generations+3):0{3}}/{(generations+3):0{3}}: animation.gif")
        frames[0].save(
            "animation.gif", 
            save_all=True, 
            append_images=(frames[1:-1]+frames[::-1][:-1]), 
            optimize=False, 
            duration=100, 
            loop=0)
    elif(out == "png"):
        print(f"{1:0{3}}/{(generations+2):0{3}}: 000.png")
        evolveImage(image, image, kernel, method, sigma).save("000.png")                #   creates first image
        for i in range(generations):                                                    #   creates transition images
            print(f"{(i+2):0{3}}/{(generations+2):0{3}}: {(i+1):0{3}}.png")
            image = evolveImage(image, enviroment, kernel, method, sigma)               #   creates generation n image
            image.save(f"{(i+1):0{3}}.png")
        print(f"{(generations+2):0{3}}/{(generations+2):0{3}}: {(generations+1):0{3}}.png")
        evolveImage(enviroment, enviroment, kernel, method, sigma).save(f"{(generations+1):0{3}}.png")  #   creates final image
    else:
        print(f"Output argument not recognized - quitting: {out}")

    image.close()
    enviroment.close()


if(__name__=="__main__"): main()                                #   runs main if run directly
else: pass                                                      #   pass if loaded as module