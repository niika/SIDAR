import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

exec(compile(open(path+"/"+"objects.py").read(), filename, 'exec'))


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


def render_ground_truth(camera = "Camera0", image_path="output.png"):

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



def render_ambient(camera = "Camera0", image_path="output.png"):
    
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

