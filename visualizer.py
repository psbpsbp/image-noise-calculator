from PIL import Image
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
from texturepacker import distribution,wrap_x,wrap_y,adaptative,gradient



#a list with all the addresses of the images you want to visualize (you can use r"" if backslashes are affecting the string)
textures = []


#a multiplier for the size of the final image
mult=40







def noisemapvis(ftexture: Image, pls: list[list[int]]):
  ts = ftexture.size
  canva = Image.new("LA", size=ts, color=(0, 0))
  ldt = ftexture.load()
  edcanva = canva.load()
  extremes = [255, 0] if adaptative else [0, 255]

  for px in range(ts[0]):

    for py in range(ts[1]):

      if ldt[px, py][3] != 0:

        pnoise = 0
        totalval = 0
        for pl in pls:

          if (ldt[(px + pl[0]) % ts[0], (py + pl[1]) % ts[1]][3] == 0) or (not wrap_x and not (0 < px + pl[0] < ts[0])) or (not wrap_y and not (0 < py + pl[1] < ts[1])):
            continue

          for col in (0, 1, 2):
            pnoise += abs(ldt[px, py][col] - ldt[(px + pl[0]) % ts[0], (py + pl[1]) % ts[1]][col]) * pl[2]

          totalval += pl[2]

        pnoise = int(pnoise / (3 * totalval)) if totalval != 0 else 0
        if pnoise < extremes[0]: extremes[0] = pnoise
        if pnoise > extremes[1]: extremes[1] = pnoise
        edcanva[px, py] = (pnoise, ldt[px, py][3])

  palette = []
  ext = (extremes[1] - extremes[0]) if (extremes[1] - extremes[0] >= 0) else 0
  fgradient = plt.get_cmap(gradient, ext)

  for i in range(256):

    if extremes[0] <= i <= extremes[1]:
      g = fgradient((i - extremes[0]) / (ext if ext != 0 else 1))
      palette.extend([int(g[0] * 255), int(g[1] * 255), int(g[2] * 255)])

    else:
      palette.extend([0, 0, 0])

  final = Image.new("RGBA", ts)
  for px in range(ts[0]):

    for py in range(ts[1]):
      final.load()[px, py] = (
      palette[edcanva[px, py][0] * 3], palette[edcanva[px, py][0] * 3 + 1], palette[edcanva[px, py][0] * 3 + 2],
      edcanva[px, py][1])

  return final,canva

def avgnoise(img:Image):

  img=img.convert("LA")
  imgl=img.load()
  noise=0
  tval=0
  for x in range(img.size[0]):

    for y in range(img.size[1]):

      noise+=imgl[x,y][0]*imgl[x,y][1]
      tval+=imgl[x,y][1]

  noise=noise/tval
  return noise

textures=[os.path.normpath(texturep) for texturep in textures]

fig,ax=plt.subplots(figsize=(0.05*mult,len(textures)*0.03*mult))
ax.set_xlim(0,5*mult)
ax.set_ylim(0,len(textures)*3*mult)

for texture in tqdm(range(len(textures))):

  noisemp,cnva=noisemapvis((Image.open(os.path.normpath(textures[texture]))).convert("RGBA"),distribution)

  ax.imshow(noisemp,extent=[0,2*mult,texture*3*mult,texture*3*mult+2*mult],aspect=1)
  ax.imshow((Image.open(os.path.normpath(textures[texture]))).convert("RGBA"),extent=[3*mult,5*mult,texture*3*mult,texture*3*mult+2*mult],aspect=1)
  ax.text(0,texture*3*mult+2.575*mult,textures[texture].split(os.path.dirname(textures[texture]))[1],fontsize=0.2*mult)
  ax.text(0,texture*3*mult+2.125*mult,"average noise: "+str(avgnoise(cnva)),fontsize=0.2*mult)

plt.axis("off")
plt.show()