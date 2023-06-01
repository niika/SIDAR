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



# HACK to import additional scripts 
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
        ids = [len(imgs)]

    for i in range(*ids):
        print("Rendering:", images_paths[i])
        generate_sequence(img_file=os.path.join(dirs[i], imgs[i]), dst=os.path.join(dst,str(i)), **kwargs)



    
def generate_sequence(img_file, dst = "distortions/", n_cameras = 50, homography=False, n_lights=[2,5], n_objects=[0,3], **kwargs ):
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
    render_ambient("Camera0", os.path.join(dst,"gt.png"))

    if homography:
        for cam_i in range(n_cameras+1):
            for cam_j in range(cam_i+1, n_cameras+1):
                H_ij = get_homography(f"Camera{cam_i}",f"Camera{cam_j}")
                np.savetxt(dst+f"/H_{cam_i}_{cam_j}.mat", H_ij)
    
    for j in range(n_cameras+1):
        generate_scene(img_file, n_lights, n_objects)
        camera = f"Camera{j}" if homography else "Camera0"
        render(camera, dst +"/{}.png".format(j))
        render_mask(camera, dst +"/{}-m.png".format(j))
    


                

bpy.context.scene.render.engine = 'CYCLES'
    
n = 50010
#generate_image((n,n+1000), "DIAR-Eval/")    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=True)    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=False)    



with open("config.yml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
        print(config["src"])
        print(config)        
        generate_dataset_wikiart(ids=(n,n+1),**config)

    except yaml.YAMLError as exc:
        print(exc)


#blender --background --python


