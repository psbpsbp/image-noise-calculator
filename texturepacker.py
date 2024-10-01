from PIL import Image
from tqdm import tqdm
import os
import shutil
import matplotlib.pyplot as plt



#where you want to take the textures from  (must be a directory)
read_dir = r""


#where you want to save the textures to  (must be a directory)
save_dir = r""


#the distribution used to calculate the noise maps
#must be a list made of lists with three numbers each, the first ones are the x and y offsets of the pixel whose values you want to compare
#the third one is how much weight that comparison has on the final result
distribution=[[0,-3,0.0498],[1,-2,0.0498],[-1,-2,0.0498],[-2,-1,0.0498],[2,-1,0.0498],[-3,0,0.0498],[3,0,0.0498],[-2,1,0.0498],[2,1,0.0498],[-1,2,0.0498],[1,2,0.0498],[0,-3,0.0498],[0,-2,0.3679],[1,-1,0.3679],[-1,-1,0.3679],[2,0,0.3679],[-2,0,0.3679],[1,1,0.3679],[-1,1,0.3679],[0,2,0.3679],[0,1,1],[1,0,1],[0,-1,1],[-1,0,1]]


#specifies if the pixels wrap around if the pixel they want to compare with is outside the image (boolean)
wrap_x,wrap_y=True,True


#specifies if the gradient adapts to the highest and lowest values of each noisemap (boolean)
adaptative=True


#the name of the gradient the final image will be output with (possible gradients: https://matplotlib.org/stable/users/explain/colors/colormaps.html)
gradient="viridis"

#overwite files if they already exist, change to false if you have already ran it once and just have added some new textures (boolean)
overwrite=True







def noisemap(texture: Image, pls: list[list[int]]):
  ts = texture.size
  canva = Image.new("LA", size=ts, color=(0, 0))
  ldt = texture.load()
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

    if extremes[0] <= i <= extremes[1] and ext!=0:
      g = fgradient((i - extremes[0]) / ext)
      palette.extend([int(g[0] * 255), int(g[1] * 255), int(g[2] * 255)])

    else:
      palette.extend([0, 0, 0])

  final = Image.new("RGBA", ts)
  for px in range(ts[0]):

    for py in range(ts[1]):
      final.load()[px, py] = (
      palette[edcanva[px, py][0] * 3], palette[edcanva[px, py][0] * 3 + 1], palette[edcanva[px, py][0] * 3 + 2],
      edcanva[px, py][1])

  return final

def get_files(fdir):

  files=[]

  for file in tqdm(os.listdir(fdir)):

    filedir = os.path.normpath(fdir+"\\"+file)

    if os.path.isdir(filedir):

      files=files+get_files(filedir)

    else:

      files=files+[filedir]

  return files

def save_pngs(sdir,rddir):

  for file in tqdm(get_files(rddir)):

    if not os.path.exists(os.path.dirname(spath:=os.path.normpath(sdir+file.split(rddir)[1]))):
      os.makedirs(os.path.dirname(spath))

    if not overwrite and os.path.exists(spath): continue

    if file.endswith(".png"):
      noisemap(Image.open(file).convert("RGBA"),distribution).save(spath,"PNG")

    else:
      shutil.copy(file,spath)

if __name__ == "__main__":

  read_dir,save_dir=os.path.normpath(read_dir),os.path.normpath(save_dir)

  save_pngs(save_dir,read_dir)
