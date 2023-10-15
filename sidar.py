import bpy
from mathutils import Vector
import numpy as np
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
from bpy_extras.image_utils import load_image
from mathutils import Color
import glob 
import os
import sys
import yaml
import argparse



# HACK to import additional scripts into blender's python environment
# https://docs.blender.org/api/current/info_tips_and_tricks.html
full_path = os.path.realpath(__file__)
path,_ = os.path.split(full_path)
filename = "materials.py"
exec(compile(open(path+"/"+"objects.py").read(), "objects", 'exec'))
exec(compile(open(path+"/"+"scene.py").read(), "scene", 'exec'))
exec(compile(open(path+"/"+"render.py").read(), "render", 'exec'))
exec(compile(open(path+"/"+"homography.py").read(), "homography", 'exec'))


def generate_dataset_wikiart(src="wikiart/", dst = "SIDAR/",  ids=None,  **kwargs ):

    images_paths = glob.glob(src+"/*/*")
    images_paths.sort()
    images_paths = [os.path.split(path) for path in images_paths]
    dirs, imgs = list(zip(*images_paths))
    
    with open(os.path.join(dst,"imgs.txt"), 'w') as fp:
        for i,item in enumerate(images_paths):
            # write each item on a new line
            fp.write("%d:%s\n" % (i,item))
    
    if ids is None:
        ids = range(len(imgs))

    for i in ids:
        try:
            print("Rendering:", images_paths[i])

            bpy.data.images.load(os.path.join(dirs[i], imgs[i]))
            bpy.data.images[0].name = 'painting'
            x,y = bpy.data.images['painting'].size
            print(x*y)
            if x*y > 4*1e6:
                continue
            generate_sequence(img_file=os.path.join(dirs[i], imgs[i]), dst=os.path.join(dst,str(i)), **kwargs)
        except:
            print(f"Error in id= {i}")



    
def generate_sequence(img_file, dst = "distortions/", n_cameras = 50, homography=False, n_lights=[2,5],
                       n_objects=[0,3], ambient=False, visible = True, **kwargs ):
    """_summary_

    Args:
        img_file (str): path to image file
        dst (str, optional): destination directory. Defaults to "distortions/".
        n_cameras (int, optional): number of cameras to generate. This also describes the number of generated images. Defaults to 50.
        homography (bool, optional): W Defaults to False.
    """

    add_plane(img_file)
    if homography:
        add_cameras(n_cameras)
    add_front_camera("Camera0")
    render_ground_truth("Camera0", os.path.join(dst,"gt.png"))

    if homography:
        for cam_i in range(n_cameras+1):
            for cam_j in range(cam_i+1, n_cameras+1):
                H_ij = get_homography(f"Camera{cam_i}",f"Camera{cam_j}")
                np.savetxt(dst+f"/H_{cam_i}_{cam_j}.mat", H_ij)
    
    for j in range(n_cameras+1):
        generate_scene(img_file, n_lights, n_objects,visible)
        camera = f"Camera{j}" if homography else "Camera0"
        if ambient:
            render_ambient(camera, dst +"/{}.png".format(j))
        else:
            render(camera, dst +"/{}.png".format(j))
        render_mask(camera, dst +"/{}-m.png".format(j))
    


                

bpy.context.scene.render.engine = 'CYCLES'
    
n = 50010
#generate_image((n,n+1000), "DIAR-Eval/")    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=True)    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=False)    

argv = sys.argv

argv = argv[argv.index("--") + 1:]  # get all args after "--"
parser = argparse.ArgumentParser(description='Adding lights, shadows and occlusions using Blender')
parser.add_argument('--src', help='source image')
parser.add_argument('--dst', help='source image')
parser.add_argument('--n_cameras', metavar='N', type=int, default= 10,
                    help='number of cameras')
parser.add_argument('--n_lights', metavar='L', type=int, default= [2,5], nargs=2,
                    help='number of lights')
parser.add_argument('--n_objects', metavar='O', type=int, default= [0,4], nargs=2,
                    help='number of objects')
parser.add_argument('--homography', dest='homography', action='store_true', default=False)
args = parser.parse_args(argv)
print(args.n_lights)

with open("config.yml", "r") as stream:
    try:
        config = yaml.safe_load(stream)

        ids = np.random.randint(0,81444, 3000)
        print(ids)
        print(argv)
        print(config["src"])
        print(config)        
        generate_dataset_wikiart(ids=ids,**config)

    except yaml.YAMLError as exc:
        print(exc)

# blender -b --python sidar.py -- <Command line arguments >
# blender -b --python sidar.py


