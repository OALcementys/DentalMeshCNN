##import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl
import numpy as np
import polyscope as ps
import numpy as np
import os
#import polyscope as ps
import random
#import OpenGL
#import OpenGL.GL
#import OpenGL.GLUT
#import OpenGL.GLU
##################################
'''
We used polyscope for visualising results , for starters we extracted predicted classes of edges from the obj test file
then we visualize the results'''
V = np.array
r2h = lambda x: colors.rgb2hex(tuple(map(lambda y: y / 255., x)))
surface_color = r2h((255, 230, 205))
edge_color = r2h((90, 90, 90))
edge_colors = (r2h((15, 167, 175)), r2h((230, 81, 81)), r2h((142, 105, 252)), r2h((248, 235, 57)),
                r2h((225, 117, 231)))
def parse_obje(obj_file, scale_by):
    vs = []
    faces = []
    edges = []

    def add_to_edges():
        if edge_c >= len(edges):
            for _ in range(len(edges), edge_c + 1):
                edges.append([])
        edges[edge_c].append(edge_v)

    def fix_vertices():
        nonlocal vs, scale_by
        vs = V(vs)
        z = vs[:, 2].copy()
        vs[:, 2] = vs[:, 1]
        vs[:, 1] = z
        max_range = 0
        for i in range(3):
            min_value = np.min(vs[:, i])
            max_value = np.max(vs[:, i])
            max_range = max(max_range, max_value - min_value)
            vs[:, i] -= min_value
        if not scale_by:
            scale_by = max_range
        vs /= scale_by

    with open(obj_file) as f:
        for line in f:
            line = line.strip()
            splitted_line = line.split()
            if not splitted_line:
                continue
            elif splitted_line[0] == 'v':
                vs.append([float(v) for v in splitted_line[1:]])
            elif splitted_line[0] == 'f':
                faces.append([int(c) - 1 for c in splitted_line[1:]])
            elif splitted_line[0] == 'e':
                if len(splitted_line) >= 4:
                    edge_v = [int(c) - 1 for c in splitted_line[1:-1]]
                    edge_c = int(splitted_line[-1])
                    add_to_edges()

    vs = V(vs)
    fix_vertices()
    faces = V(faces, dtype=int)
    edges = [V(c, dtype=int) for c in edges]
    return (vs, faces, edges), scale_by
#####################################################################
def view_mesh(file):
    scale = 0
    mesh, scale = parse_obje(file, scale)
    global edg_ly
    vs, face, edg_ly = mesh
    global edges
    edges=np.concatenate([edg_ly[i] for i in range(len(edg_ly))])
    #edges=edgly[0]
    verts,faces=np.array(vs),np.array(face)
    global nodes
    nodes = np.array(verts)
    ps.init()
    radius=0.0015
        # register a curve network
    ps_net = ps.register_curve_network("Maillage", nodes, edges,radius=radius,enabled=True)
    global vals_edge
    vals_edge= []
    color_list=[[1,0,0],[0,1,0],[1,1,0],[0,0,1],[0,0,0]]
    for i in range(len(edg_ly)):
        color=np.ones((len(edg_ly[i]),3))*color_list[i]
        vals_edge.append(color)
    val_edge=np.concatenate([vals_edge[i] for i in range(len(edg_ly))])
    ps_net.add_color_quantity("Mesh Segmentation", val_edge, defined_on='edges')
    names=["Incisives","canines","prémolaires","molaires","base"]
    for i in range(len(names)):
        ps_net = ps.register_curve_network(names[i], nodes, edg_ly[i],radius=0.0015)
        ps_net.add_color_quantity(names[i], vals_edge[i], defined_on='edges',enabled=False)


    ps.show()



if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser("view meshes")
    parser.add_argument('--files', nargs='+', default=[r"C:\Users\ASUS\Desktop\MeshCNN-master\checkpoints\human_seg\meshes\Copie_de_af_stage_5_of_11_lower_hori__tr4_2.obj"],
               type=str,help="list of 1 or more .obj files")
    args = parser.parse_args()

    # view meshes
    view_mesh(*args.files)
