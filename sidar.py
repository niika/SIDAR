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

def get_homography(camera1, camera2):
    
    # get corner points
    obj = bpy.data.objects['Plane'] 
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        vertices = bm.verts

    else:
        vertices = obj.data.vertices

    verts = [obj.matrix_world @ vert.co for vert in vertices] 
    
    scene = bpy.context.scene
    camera1 = bpy.data.objects[camera1]
    scene.camera = camera1
    render = bpy.context.scene.render
    proj1 = [project_3d_point(camera=camera1, p=P, render=render) for P in verts]
    
    scene = bpy.context.scene
    camera2 = bpy.data.objects[camera2]
    scene.camera = camera2
    render = bpy.context.scene.render
    proj2 = [project_3d_point(camera=camera2, p=P, render=render) for P in verts]
    
    A = np.zeros((8,9))
    for i,(p1,p2) in enumerate(zip(proj1,proj2)):
        A[2*i, :] = np.array([-p1.x,-p1.y,-1,0,0,0,p1.x*p2.x,p1.y*p2.x, p2.x]) 
        A[2*i +1, :] = np.array([0,0,0,-p1.x,-p1.y,-1,p1.x*p2.y,p1.y*p2.y, p2.y])     
    u, s, vh = np.linalg.svd(A)
    
    h = vh[-1,:]
    
    H = h.reshape((3,3))
    H = H / np.cbrt(np.linalg.det(H))

    # Test
    #p1 = proj1[0]
    #p1 = np.array([p1.x,p1.y,1])
    #p2 = H @p1
    #p2 = p2/p2[2]
    #print(p2,proj2[0])
    return H



def generate_dataset_wikiart(src="wikiart/", dst = "SIAR/",  ids=None,  **kwargs ):

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

                

def project_3d_point(camera: bpy.types.Object,
                     p: Vector,
                     render: bpy.types.RenderSettings = bpy.context.scene.render) -> Vector:
    """
    Given a camera and its projection matrix M;
    given p, a 3d point to project:

    Compute P’ = M * P
    P’= (x’, y’, z’, w')

    Ignore z'
    Normalize in:
    x’’ = x’ / w’
    y’’ = y’ / w’

    x’’ is the screen coordinate in normalised range -1 (left) +1 (right)
    y’’ is the screen coordinate in  normalised range -1 (bottom) +1 (top)

    :param camera: The camera for which we want the projection
    :param p: The 3D point to project
    :param render: The render settings associated to the scene.
    :return: The 2D projected point in normalized range [-1, 1] (left to right, bottom to top)
    """

    if camera.type != 'CAMERA':
        raise Exception("Object {} is not a camera.".format(camera.name))

    if len(p) != 3:
        raise Exception("Vector {} is not three-dimensional".format(p))
        
    bpy.context.view_layer.update()
    # Get the two components to calculate M
    modelview_matrix = camera.matrix_world.inverted()
    projection_matrix = camera.calc_matrix_camera(
        bpy.data.scenes["Scene"].view_layers["ViewLayer"].depsgraph,
        x = render.resolution_x,
        y = render.resolution_y,
        scale_x = render.pixel_aspect_x,
        scale_y = render.pixel_aspect_y,
    )

    # print(projection_matrix * modelview_matrix)

    # Compute P’ = M * P

    p1 = projection_matrix @ modelview_matrix @ Vector((p.x, p.y, p.z, 1))

    # Normalize in: x’’ = x’ / w’, y’’ = y’ / w’
    #print(p1, modelview_matrix, projection_matrix)
    p2 = Vector(((p1.x/p1.w, p1.y/p1.w)))
    proj_p_pixels = Vector(((render.resolution_x-1) * (p2.x + 1) / 2, (render.resolution_y - 1) * (p2.y - 1) / (-2)))
    return proj_p_pixels


bpy.context.scene.render.engine = 'CYCLES'
    

print(sys.argv)
n = 50010
#generate_image((n,n+1000), "DIAR-Eval/")    
#generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=True)    
generate_dataset_wikiart(src="wikiart/", dst="test2/", ids= (n,n+1), n_cameras=5, homography=False)    

#blender --background --python


