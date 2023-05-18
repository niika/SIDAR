import bpy
from mathutils import Vector
import numpy as np

from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
from bpy_extras.image_utils import load_image
from mathutils import Color
import glob 
import os
import sys


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


    
    
    
def generate_sequence(ids, src="wikiart/", dst = "SIAR/", n_cameras = 50 ):

    images_paths = glob.glob(src+"*/*")
    images_paths.sort()
    images_paths = [os.path.split(path) for path in images_paths]
    dirs, imgs = list(zip(*images_paths))
    
    with open(dst+"imgs.txt", 'w') as fp:
        for i,item in enumerate(images_paths):
            # write each item on a new line
            fp.write("%d:%s\n" % (i,item))

    for i in range(*ids):
        print(images_paths[i])
        
        #if os.path.exists(dst+str(i)):
        #    continue

        add_plane(dirs[i]+"/"+imgs[i])


        
        x,y = bpy.data.images['painting'].size
        #if x*y >1000000:
            #print("Resolution too high!")
            #continue
        

        add_cameras(n_cameras)
        add_front_camera("Camera0")
        render_ambient("Camera0", dst+str(i)+"/gt.png")

        for cam_i in range(n_cameras+1):
            for cam_j in range(cam_i+1, n_cameras+1):
                H_ij = get_homography(f"Camera{cam_i}",f"Camera{cam_j}")
                np.savetxt(dst+str(i)+f"/H_{cam_i}_{cam_j}.mat", H_ij)
        
        for j in range(n_cameras+1):

            generate_scene(dirs[i]+"/"+imgs[i], [2,5], [3])

            render("Camera"+str(j), dst+str(i)+"/{}.png".format(j))
            render_mask("Camera"+str(j), dst+str(i)+"/{}-m.png".format(j))



                

    
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
        try:
            add_plane(dirs[i]+"/"+imgs[i])

            
            x,y = bpy.data.images['painting'].size
            #if x*y >1000000:
                #print("Resolution too high!")
                #continue
            

            #add_cameras(n_cameras)
            add_front_camera("Camera0")

            render_ambient("Camera0", dst+str(i)+"/gt.png")

            
            for j in range(n_cameras+1):
                add_plane(dirs[i]+"/"+imgs[i])

                n_lights = np.random.randint(1, 5)
                add_illumination(n_lights)
                n_objects = np.random.randint(0,3)
                add_objects(n_objects)
                

                render("Camera0", dst+str(i)+"/{}.png".format(j))
                render_mask("Camera0", dst+str(i)+"/{}-m.png".format(j))


        except Exception as e:
            print(e)
            print("---------Error in image {} ----------".format(i))
                

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
generate_sequence((n,n+1), dst="test2/", n_cameras=5)    
generate_sequence_aligned((50011,50012), dst="test2/", n_cameras= 5)  

add_plane("wikiart/Romanticism/lev-lagorio_crimean-landscape-1891.jpg")
add_illumination(2)
add_cameras(3)
add_front_camera()
#render_ambient(image_path="vis/gt.png")
add_objects(3)

render("Camera2", image_path="test/before-mask.png")

render_mask("Camera2", image_path="test/after-mask.png")
#render_ambient()


