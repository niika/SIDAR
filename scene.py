import bpy
import numpy as np

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
    



def generate_scene(img_path, n_lights= 5, n_objects=3):

    add_plane(img_path)
    #add_front_camera("Camera0")
    light = np.random.randint(*n_lights)
    print(light)
    add_illumination(light)
    n_objects = np.random.randint(*n_objects)
    add_objects(n_objects)