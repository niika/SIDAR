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


    
def generate_sequence(src, dst = "distortions/", n_cameras = 50, homography=False, n_lights=[2,5],
                       n_objects=[0,3], ambient=False, visible = True, **kwargs ):
    """_summary_

    Args:
        img_file (str): path to image file
        dst (str, optional): destination directory. Defaults to "distortions/".
        n_cameras (int, optional): number of cameras to generate. This also describes the number of generated images. Defaults to 50.
        homography (bool, optional): W Defaults to False.
    """

    add_plane(src)
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
        generate_scene(src, n_lights, n_objects,visible)
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
parser.add_argument('--dst', help='destination directory')
parser.add_argument('--n_cameras', metavar='N', type=int, default= 10,
                    help='number of cameras')
parser.add_argument('--n_lights', metavar='L', type=int, default= [2,5], nargs=2,
                    help='number of lights')
parser.add_argument('--n_objects', metavar='O', type=int, default= [0,4], nargs=2,
                    help='number of objects')
parser.add_argument('--homography', dest='homography', action='store_true', default=False)
args = parser.parse_args(argv)
print(args.n_lights)



#
#print(ids)
print(args)

generate_sequence(**vars(args))

        



# blender -b --python sidar.py -- <Command line arguments >
# blender -b --python sidar.py


