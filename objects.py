import bpy
import numpy as np
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper




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


def add_objects(n_obj = 3, visible=True):
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
        
        obj.visible_camera=visible
    

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

