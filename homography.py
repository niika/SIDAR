
import bpy


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

    return H

