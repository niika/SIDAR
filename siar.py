import bpy
from mathutils import Vector
import numpy as np

from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
from bpy_extras.image_utils import load_image
from mathutils import Color
import glob 
import os
import sys

def add_camera(name, tx, ty, tz):
    
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)
    #bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.collection.objects.link(camera_object)
    scene = bpy.context.scene
    scene.camera = camera_object

    fov = np.random.uniform(30,90)

    pi = 3.14159265


    # Set camera fov in degrees
    camera_data.angle = fov*(pi/180.0)

    # Set camera translation
    camera_object.location.x = tx
    camera_object.location.y = ty
    camera_object.location.z = tz
    
    v1 = Vector((0,0,1))
    v2 = camera_object.location
    rotation = v1.rotation_difference(v2).to_euler()
    camera_object.rotation_euler = rotation
    # Set camera rotation in euler angles
    #camera_object.rotation_mode = 'XYZ'
    #camera_object.rotation_euler[0] = rx*(pi/180.0)
    #camera_object.rotation_euler[1] = ry*(pi/180.0)
    #camera_object.rotation_euler[2] = rz*(pi/180.0)

    camera_data.lens = np.random.uniform(15,30)



def add_light(name, position):
    
    type = np.random.choice(["POINT","SPOT","AREA"])
    light_data = bpy.data.lights.new(name=name, type=type)
    if type == "POINT":
        light_data.energy = np.random.uniform(1000,3500)
    if type == "SPOT":
        light_data.energy = np.random.uniform(1000,10000)
        light_data.spot_size = np.random.uniform(10*np.pi/180,90*np.pi/180)
        light_data.spot_blend = np.random.uniform(0,1)
    if type == "AREA":
        light_data.energy = np.random.uniform(1000,2000)
        light_data.spread = np.random.uniform(10*np.pi/180,90*np.pi/180)
        
    c = Color()
    c.hsv = np.random.uniform(0,1),np.random.uniform(0,0.3),1
    light_data.color = c

    # Create new object, pass the light data 
    light_object = bpy.data.objects.new(name=name, object_data=light_data)

    # Link object to collection in context
    bpy.context.collection.objects.link(light_object)

    # Change light position
    light_object.location = position
    v1 = Vector((0,0,1))
    v2 = light_object.location
    rotation = v1.rotation_difference(v2).to_euler()
    light_object.rotation_euler = rotation


def add_plane(file):
    
    # Remove Materials
    for img in bpy.data.images:
        if img.name.startswith("painting"):
            bpy.data.images.remove(img)
    #remove previous plane
    for obj in bpy.data.objects:
        if obj.name.startswith("Plane"):
            bpy.data.meshes.remove(obj.data)
    
    #remove inital cube object
    for obj in bpy.data.objects:
        if obj.name.startswith("Cube"):
            bpy.data.meshes.remove(obj.data)

    # Remove Lights
    for light in bpy.data.lights:
        if light.name.startswith("Light"):
            bpy.data.lights.remove(light)
    
    bpy.ops.mesh.primitive_plane_add(align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.data.images.load(file)
    bpy.data.images[0].name = 'painting'


    x,y = bpy.data.images['painting'].size
    ratio = x/y
    
    w = 3.5
    if ratio > 1:
        bpy.data.objects['Plane'].scale = (w*ratio,w,0)
        bpy.data.objects['Plane'].rotation_euler= (0,0,0)
    else:
        bpy.data.objects['Plane'].scale = (w*ratio,w,0)
        bpy.data.objects['Plane'].rotation_euler= (0,0,-90*np.pi/180)



    # Remove Materials
    for mat in bpy.data.materials:
        if mat.name.startswith("PlaneMaterial"):
            bpy.data.materials.remove(mat)
        
    mat = principledBSDF_material("PlaneMaterial")
    #mat = diffuse_material("PlaneMaterial")
    mat.use_nodes = True
    principled = PrincipledBSDFWrapper(mat, is_readonly=False)
    #principled.base_color_texture.image = load_image("Blender/painting.jpg",check_existing= True) 
    principled.base_color_texture.image = bpy.data.images['painting']
    #principled.specular_texture.image  = bpy.data.images['painting']

    obj = bpy.data.objects['Plane']
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    #bpy.data.materials['Plane'].node_tree.nodes["Image Texture"].image =  bpy.data.images['painting']



def add_cameras(n=10):
    # Remove Cameras
    for cam in bpy.data.cameras:
        if cam.name.startswith("Camera"):
            bpy.data.cameras.remove(cam)

    # Add Random Cameras approximately looking into the image center
    
    for i in range(n):
        x = np.random.uniform(-5,5)
        y = np.random.uniform(-5,5)
        z = np.random.uniform(5,7)
        add_camera("Camera"+str(i+1), x,y,z)


def add_illumination(n_lights = 3):
    # Remove Lights
    for light in bpy.data.lights:
        if light.name.startswith("Light"):
            bpy.data.lights.remove(light)

    # Add Lights
    # Create light datablock

    for i in range(n_lights):
        
        x = np.random.uniform(-10,10)
        y = np.random.uniform(-10,10)
        z = np.random.uniform(10,15)
        add_light("Light"+str(i+1), (x,y,z))
    





def glossy_material(name ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    shader = material.node_tree.nodes.new("ShaderNodeBsdfGlossy")
    shader.inputs['Color'].default_value = np.random.uniform(0,1 , 4) 
    shader.inputs['Roughness'].default_value = np.random.uniform(0, 0.5 ) 
    # link emission shader to material
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])
    return material
    

def glass_material(name ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    shader = material.node_tree.nodes.new("ShaderNodeBsdfGlass")
    shader.inputs['Color'].default_value = np.random.uniform(0,1 , 4) 
    shader.inputs['Roughness'].default_value = np.random.uniform(0,0.5 ) 
    shader.inputs['IOR'].default_value = np.random.uniform(1,2 ) 
    # link emission shader to material
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])
    return material

def refraction_material(name ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    shader = material.node_tree.nodes.new("ShaderNodeBsdfRefraction")
    shader.inputs['Color'].default_value = np.random.uniform(0,1 , 4) 
    shader.inputs['Roughness'].default_value = np.random.uniform(0,0.5 ) 
    shader.inputs['IOR'].default_value = np.random.uniform(1,2 ) 
    # link emission shader to material
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])
    return material

def transparent_material(name ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    shader = material.node_tree.nodes.new("ShaderNodeBsdfTransparent")
    shader.inputs['Color'].default_value = np.random.uniform(0,1 , 4) 

    # link emission shader to material
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])
    return material


def principledBSDF_material(name ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    
    shader = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs['Base Color'].default_value = np.random.uniform(0,1 ,4) 
    shader.inputs['Subsurface Color'].default_value = np.random.uniform(0,1 ,4) 
    shader.inputs['Roughness'].default_value = np.random.uniform(0,0.5 ) 
    shader.inputs['IOR'].default_value = np.random.uniform(1,2 ) 
    shader.inputs['Subsurface IOR'].default_value = np.random.uniform(1,2 ) 
    # link emission shader to material
    
    shader.inputs['Metallic'].default_value = np.random.uniform(0,1) 
    shader.inputs['Specular'].default_value = np.random.uniform(0,1) 
    shader.inputs['Transmission'].default_value = np.random.uniform(0,1) 
    shader.inputs['Transmission Roughness'].default_value = np.random.uniform(0,1) 
    shader.inputs['Clearcoat'].default_value = np.random.uniform(0,1) 
    shader.inputs['Clearcoat Roughness'].default_value = np.random.uniform(0,1) 
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])

    return material

def diffuse_material(name, color=(0,0,0,1) ):
    # Create a new material
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    # Remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
    material_output = material.node_tree.nodes.get('Material Output')
    nodes = material.node_tree.nodes
    
    shader = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Subsurface Color'].default_value = (0,0,0,1)
    shader.inputs['Roughness'].default_value = 1
    shader.inputs['IOR'].default_value = 0
    shader.inputs['Subsurface IOR'].default_value = 0
    # link emission shader to material
    
    shader.inputs['Metallic'].default_value = 0
    shader.inputs['Specular'].default_value = 0
    shader.inputs['Transmission'].default_value = 0
    shader.inputs['Transmission Roughness'].default_value = 0
    shader.inputs['Clearcoat'].default_value = 0
    shader.inputs['Clearcoat Roughness'].default_value = 0
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])

    return material


def add_objects(n_obj = 3):
    # Remove Materials
    for mat in bpy.data.materials:
        if mat.name.startswith("ObjMaterial"):
            bpy.data.materials.remove(mat)

    #remove objects
    for obj in bpy.data.objects:
        if obj.name.startswith("Object"):
            bpy.data.meshes.remove(obj.data)
            
    #remove inital cube object
    for obj in bpy.data.objects:
        if obj.name.startswith("Cube"):
            bpy.data.meshes.remove(obj.data)

        
    for i in range(n_obj):

        x = np.random.uniform(-3,3)
        y = np.random.uniform(-3,3)
        z = np.random.uniform(1,5)
        rx,ry,rz = np.random.uniform(0,2*np.pi, 3)
        scale = np.random.uniform(0.1,1.1, 3) 
        
        shape = np.random.choice(["Cone", "Sphere", "Cylinder", "Torus", "Cube"])
        
        if shape == "Cone":
            bpy.ops.mesh.primitive_cone_add(vertices= 300, location = (x,y,z),scale = scale, rotation=(rx,ry,rz))
        elif shape == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(segments=100, ring_count=100, scale = scale,location = (x,y,z), rotation=(rx,ry,rz))
        elif shape == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(vertices= 200, location = (x,y,z),scale = scale, rotation=(rx,ry,rz))
        elif shape == "Torus":
            bpy.ops.mesh.primitive_torus_add(major_segments=100, minor_segments=50, location = (x,y,z), rotation=(rx,ry,rz))
        elif shape =="Cube":
            bpy.ops.mesh.primitive_cube_add(location = (x,y,z),scale = scale, rotation=(rx,ry,rz))
        
        # Rename objects
        obj = bpy.context.active_object
        obj.name= "Object"+str(i+1)
        obj.data.name= "Object"+str(i+1)
        
        # Change Material
        material  = np.random.choice(["Glossy", "Transparent", "Refraction", "Glass", "Principled"])
        if material == "Glossy":
            mat = glossy_material("ObjMaterial"+str(i))
        elif material == "Transparent":
            mat = transparent_material("ObjMaterial"+str(i))
        elif material == "Refraction":
            mat = refraction_material("ObjMaterial"+str(i))
        elif material == "Glass":
            mat = glass_material("ObjMaterial"+str(i))
        else:
            mat = principledBSDF_material("ObjMaterial"+str(i))
        obj.data.materials.append(mat)
    
    

def add_front_camera(name="Camera0", tx=0, ty=0, tz=10):
        # Remove Cameras
    for cam in bpy.data.cameras:
        if cam.name.startswith(name):
            bpy.data.cameras.remove(cam)
            
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)
    #bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.collection.objects.link(camera_object)
    scene = bpy.context.scene
    scene.camera = camera_object

    #fov = np.random.uniform(30,90)
    fov =30
    pi = 3.14159265


    # Set camera fov in degrees
    #camera_data.angle = fov*(pi/180.0)

    # Set camera translation
    camera_object.location.x = 0
    camera_object.location.y = 0
    camera_object.location.z = 10
    
    v1 = Vector((0,0,1))
    v2 = camera_object.location
    rotation = v1.rotation_difference(v2).to_euler()
    camera_object.rotation_euler = rotation
    # Set camera rotation in euler angles
    #camera_object.rotation_mode = 'XYZ'
    #camera_object.rotation_euler[0] = rx*(pi/180.0)
    #camera_object.rotation_euler[1] = ry*(pi/180.0)
    #camera_object.rotation_euler[2] = rz*(pi/180.0)

    #camera_data.lens = np.random.uniform(15,30)
    
    x,y = bpy.data.images['painting'].size

    ratio = x/y
    
    image_width = 7.0
    print(x,y)
    if ratio > 1:
        print("ratio > 1")
        #bpy.data.objects['Plane'].scale = (w*ratio,w,0)
        #bpy.data.objects['Plane'].rotation_euler= (0,0,0)
        scene.render.resolution_x = x
        scene.render.resolution_y = y
        
        sensor_width = camera_data.sensor_width / ratio
        
        camera_data.lens = 10.0*sensor_width/image_width
        
        
        #theta = 2*np.arctan(image_width/20)
        #camera_data.angle = 2*np.arctan(w/10)*(180/pi)
        #hfov = 2 * np.arctan((0.5 * x) / (0.5 * y / np.tan(theta/2)))
        #camera_data.lens = d/(4*np.tan(hfov/2))

        
        
        
    else:
        print("ratio < 1")
        scene.render.resolution_x = y
        scene.render.resolution_y = x
        
        sensor_width = camera_data.sensor_width
        camera_data.lens = 10.0*sensor_width/image_width
        
        
        #theta = 2*np.arctan(w/20)
        #camera_data.angle = 2*np.arctan(w/10)*(180/pi)
        #camera_data.lens = d/(4*np.tan(theta/2))

        #bpy.data.objects['Plane'].scale = (w*ratio,w,0)
        #bpy.data.objects['Plane'].rotation_euler= (0,0,-90*np.pi/180)


def render(camera = "Camera0", image_path="output.png"):
    
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.scene.view_settings.view_transform = 'Standard'
    scene = bpy.context.scene
    scene.camera = bpy.data.objects[camera]

    #scene.render.resolution_x = 512
    #scene.render.resolution_y = 334
    bpy.context.scene.render.engine = 'CYCLES'
    scene.cycles.time_limit= 1
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath = image_path
    bpy.ops.render.render(write_still=1)
############## Render #################


def render_ambient(camera = "Camera0", image_path="output.png"):

     # Remove Materials
    for mat in bpy.data.materials:
        if mat.name.startswith("ObjMaterial"):
            bpy.data.materials.remove(mat)

    #remove objects
    for obj in bpy.data.objects:
        if obj.name.startswith("Object"):
            bpy.data.meshes.remove(obj.data)  
            
    for light in bpy.data.lights:
        if light.name.startswith("Light"):
            bpy.data.lights.remove(light)
    
    


    obj = bpy.data.objects['Plane']
    mat = diffuse_material("PlaneMaterial")
    principled = PrincipledBSDFWrapper(mat, is_readonly=False) 
    principled.base_color_texture.image = bpy.data.images['painting']
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    
    
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'  
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    bpy.context.scene.view_settings.view_transform = 'Standard'

    scene = bpy.context.scene
    scene.camera = bpy.data.objects[camera]

    scene.cycles.time_limit= 1
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath = image_path
    bpy.ops.render.render(write_still=1)


def render_mask(camera = "Camera0", image_path="output.png"):

    # Remove Materials
    for mat in bpy.data.materials:
        if mat.name.startswith("ObjMaterial") or mat.name.startswith("Plane"):
            bpy.data.materials.remove(mat)

    #change material objects to perfectly diffuse white
    for obj in bpy.data.objects:
        if obj.name.startswith("Object"):
            #bpy.data.meshes.remove(obj.data)  

            mat = diffuse_material("ObjMaterial0",color=(1,1,1,1))
            obj.data.materials.clear()
            obj.data.materials.append(mat)
    
    # remove lights
    for light in bpy.data.lights:
        if light.name.startswith("Light"):
            bpy.data.lights.remove(light)
    
    obj = bpy.data.objects['Plane']
    mat = diffuse_material("PlaneMaterial")
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 0)
    bpy.context.scene.view_settings.view_transform = 'Standard'

    scene = bpy.context.scene
    scene.camera = bpy.data.objects[camera]
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    scene.render.image_settings.file_format='PNG'
    scene.render.filepath = image_path
    bpy.ops.render.render(write_still=1)


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



def generate_scene(img_path, n_cameras=10, n_lights= 5):
    add_plane(img_path)
    add_cameras(n_cameras)
    add_front_camera("Camera0")
    light = np.random.randint(1, n_lights)
    add_illumination(n_lights)
    n_objects = 2
    add_objects(n_objects)
    
    
    
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
        
        if os.path.exists(dst+str(i)):
            continue
        try:
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
                add_plane(dirs[i]+"/"+imgs[i])
                n_lights = np.random.randint(2, 5)
                add_illumination(n_lights)
                n_objects = np.random.randint(0,3)
                add_objects(n_objects)
                

                render("Camera"+str(j), dst+str(i)+"/{}.png".format(j))
                render_mask("Camera"+str(j), dst+str(i)+"/{}-m.png".format(j))
                #render("CameraFront", dir+str(i)+"/{}.png".format(j))
                #render("CameraFront","DIAR/"+str(i)+"/front2.png")

        except Exception as e:
            print(e)
            print("---------Error in image {} ----------".format(i))
                

    
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


