#!/usr/bin/python3
#
################################################################################################################################
#  name:  noah olmstead harvey
#  date:  24012021
#  idea:  this script evolves an image using another image as selection pressure
################################################################################################################################

####  IMPORTS  #################################################################################################################

from PIL import Image
from random import gauss

####  FUNCTIONS  ###############################################################################################################

def evolveImage(img,env):
    nextGen = Image.new("RGB", (img.size[0],img.size[1]), (0,0,0))              #  alpha channel for population/suitability
    for pixel in range(img.size[0] * img.size[1]):
        x,y = (pixel % img.size[0]),(pixel // img.size[1])
        newPixel = generatePixel(img, env, (x,y), img.size[0], img.size[1])
        nextGen.putpixel((x,y), newPixel)
    return(nextGen)

def generatePixel(img,env,pix,w,h):
    x,y = pix[0],pix[1]
    xNEdge,xPEdge,yNEdge,yPEdge = ((x - 1) in range(w)),((x + 1) in range(w)),((y - 1) in range(h)),((y + 1) in range(h))
    possibleAdjacent =  (((xNEdge and yNEdge),((x-1),(y-1))),(yNEdge,(x,(y-1))),((xPEdge and yNEdge),((x+1),(y-1))),
                        (xNEdge,((x-1),y)),(xPEdge,((x+1),y)),
                        ((xNEdge and yPEdge),((x-1),(y+1))),(yPEdge,(x,(y+1))),((xPEdge and yPEdge),((x+1),(y+1))))
    actualAdjacent = [i[1] for i in possibleAdjacent if i[0]]
    #print(pix,possibleAdjacent,actualAdjacent)
    childRGB = []
    #suitability = 0                                            #  for aplha channel
    for color in range(3):
        envPressure = [(abs(env.getpixel(p)[color] - img.getpixel(p)[color]),img.getpixel(p)[color]) for p in actualAdjacent]
        bestMatch = sorted(envPressure)[0][1]
        child = int(((img.getpixel(pix)[color] + bestMatch) / 2) * gauss(1, 0.1))
        if(child > 255): child = 255
        childRGB.append(child)
        #suitability += abs(env.getpixel(p)[color] - child)
        #print(childRGB)
    return(tuple(childRGB))
    #return(tuple(childRGB.append(abs(255 - suitability))))

#def mutate(rate=.1):
#    return(uniform((1 - rate), (1 + rate)))

def main():
    image = Image.open("./trex.png")
    enviroment = Image.open("./chic.png")
    generations = 16

    for i in range(generations):
        image = evolveImage(image, enviroment)
        image.save(f"{i:0{3}}.png")

    image.close()
    enviroment.close()

####  MAIN  ####################################################################################################################

if(__name__=="__main__"): main()