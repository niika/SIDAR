import bpy
from mathutils import Vector
import numpy as np
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
from bpy_extras.image_utils import load_image
from mathutils import Color
import glob 
import os
import sys



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

    images_paths = glob.glob(src+"*/*")
    images_paths.sort()
    images_paths = [os.path.split(path) for path in images_paths]
    dirs, imgs = list(zip(*images_paths))
    
    with open(dst+"imgs.txt", 'w') as fp:
        for i,item in enumerate(images_paths):
            # write each item on a new line
            fp.write("%d:%s\n" % (i,item))
    
    if ids is None:
        ids = [len(imgs)]

    for i in range(*ids):
        print("Rendering:", images_paths[i])
        generate_sequence(dirs[i]+"/"+imgs[i], f"{dst}/{i}/", **kwargs)



    
def generate_sequence(img_file, dst = "distortions/", n_cameras = 50, homography=False ):
    
    add_plane(img_file)
    if homography:
        add_cameras(n_cameras)
    add_front_camera("Camera0")
    render_ambient("Camera0", dst+"/gt.png")

    if homography:
        for cam_i in range(n_cameras+1):
            for cam_j in range(cam_i+1, n_cameras+1):
                H_ij = get_homography(f"Camera{cam_i}",f"Camera{cam_j}")
                np.savetxt(dst+f"/H_{cam_i}_{cam_j}.mat", H_ij)
    
    for j in range(n_cameras+1):
        generate_scene(img_file, [2,5], [3])
        camera = f"Camera{j}" if homography else "Camera0"
        render(camera, dst +"/{}.png".format(j))
        render_mask(camera, dst +"/{}-m.png".format(j))
    



                

    
def generate_sequence_aligned(ids, src="wikiart/",  dst =  "DIAR/", n_cameras = 50 ):
    """ Generate a sequence of distorted images without perspective distortions

    Args:
        ids (_type_): _description_
        dir (str, optional): _description_. Defaults to "DIAR/".
        n_cameras (int, optional): _description_. Defaults to 50.
    """
    
    images_paths = glob.glob(src+"*/*")
    images_paths.sort()
    images_paths = [os.path.split(path) for path in images_paths]
    dirs, imgs = list(zip(*images_paths))

    with open(dst+"imgs.txt", 'w') as fp:
        for i,item in enumerate(images_paths):
            # write each item on a new line
            fp.write("%d:%s\n" % (i,item))

    for i in range(*ids):
        print("Rendering image:", images_paths[i])
        
        if os.path.exists(dst+str(i)):
            continue

        add_plane(dirs[i]+"/"+imgs[i])
        add_front_camera("Camera0")
        render_ambient("Camera0", dst+str(i)+"/gt.png")

        
        for j in range(n_cameras+1):
            add_plane(dirs[i]+"/"+imgs[i])
            generate_scene(dirs[i]+"/"+imgs[i], [2,5], [3])
            render("Camera0", dst+str(i)+"/{}.png".format(j))
            render_mask("Camera0", dst+str(i)+"/{}-m.png".format(j))

                

bpy.context.scene.render.engine = 'CYCLES'
    

print(sys.argv)
n = 50010
#generate_image((n,n+1000), "DIAR-Eval/")    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=True)    
generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=False)    


#blender --background --python


