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
from kivy.lang import Builder
import kivy
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.uix.modalview import ModalView
from kivy.config import ConfigParser
from kivy.uix.settings import Settings

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

def view_mesh(file):
    scale = 0
    mesh, scale = parse_obje(file, scale)
    vs, face, edg_ly = mesh
    edges=np.concatenate([edg_ly[i] for i in range(len(edg_ly))])
    verts,faces=np.array(vs),np.array(face)
    nodes = np.array(verts)
    ps.init()
    radius=0.0015
        # register a curve network
    ps_net = ps.register_curve_network("my network", nodes, edges,radius=radius)
    vals_edge= []
    color_list=[[1,0,0],[0,1,0],[1,1,0],[0,0,1],[0,0,0]]
    for i in range(len(edg_ly)):
        color=np.ones((len(edg_ly[i]),3))*color_list[i]
        vals_edge.append(color)
    val_edge=np.concatenate([vals_edge[i] for i in range(len(edg_ly))])
    ps_net.add_color_quantity("Mesh Segmentation", val_edge, defined_on='edges')
    ps.show()




class MainMenu(Screen):
    name = StringProperty('main_menu')

#########################

class SecondWindow(Screen):
    id1 = ObjectProperty()
    id2 = ObjectProperty()
    label1 = ObjectProperty()
    label2 = ObjectProperty()
    L = []
    min_a = 3000
    max_a = 0
    min_b = 100000000
    max_b = -100000000
    def change_label_text(self):
        self.label1.text = "[size=30]" + "Année : " + self.id1.text + "[/size]"
        self.label2.text = "[size=30]" + "Demande : " + self.id2.text + "[/size]"
        L.append([self.id1.text, self.id2.text])
        return(L)

    def load_list(self):
        view = ModalView(size_hint = (0.75, 0.75))

        self.change_label_text().pop()
        print(L)
        for i in range(0, len(L)):
            a, b = L[i][0], L[i][1]
            a, b = int(a), int(b)
            if a < self.min_a:
                self.min_a = a
            if a > self.max_a:
                self.max_a = a
            if b < self.min_b:
                self.min_b = b
            if b > self.max_b:
                self.max_b = b
            R.append((a, b))

        graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5,
              x_ticks_major=25, y_ticks_major=1,
              y_grid_label=True, x_grid_label=True, padding=5,
              x_grid=True, y_grid=True, xmin=self.min_a, xmax=self.max_a, ymin=self.min_b, ymax=self.max_b)
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = R
        graph.add_plot(plot)

        view.add_widget(graph)
        view.open()

#########################

class WindowManager(ScreenManager):
    pass

#########################

class LoadDialog(Screen):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def show_load_list(self):
        content = LoadDialog(load=self.load_list, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a file list", content=content, size_hint=(1, 1))
        self._popup.open()

    def plot_add_ticker(self, i):
        tickers_on_plot.append(ticker_list[i])
    def plot_cancel_ticker(self, i):
        tickers_on_plot.pop(i)
    def dismiss_popup(self):
        self._popup.dismiss()


    def load_list(self, path, filename):
        global file
        file=os.path.join(path, filename[0])
        print(file)


    def dismiss_popup(self):
        self._popup.dismiss()
class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

########################



class GraphWindow(Screen):

    def Show(self):
        view_mesh(file)

    def save(self):
        export_file_path =file.replace('.dsx','.xlsx')
        df.to_excel (export_file_path, index = False, header=True)




########################################################################################
class TestApp(App):

    def build(self):
        return Builder.load_string("""
WindowManager:
    MainMenu:
    SecondWindow:
    LoadDialog:
    GraphWindow:


<MainMenu>:
    name : "main"
    BoxLayout:
        canvas.before:
            BorderImage:
                border: 10, 10, 10, 10
                source: r"3DSMARTFACTORY.png"
                pos: self.pos
                size: self.size


        Button:
            text: 'Importer Votre Mesh 3D sous format obj'
            background_color : 0,0.2,0.3,0.7
            size_hint_y: .2
            pos_hint: {'x': .3, 'y': .3}
            on_release:
                app.root.current = "first"




<SecondWindow>:
    name : "second"
    id1 : id1
    id2 : id2
    label1 : label1
    label2 : label2
    BoxLayout:
        orientation : "vertical"

        BoxLayout:
            canvas.before:
                BorderImage:
                    border: 10, 10, 10, 10
                    source: 'Images\image2.png'
                    pos: self.pos
                    size: self.size
            graph:
            size_hint_y : None
            height : "40dp"
            TextInput:
                id : id1
                text : 'Année'
                size_hint_x : 2

            TextInput:
                id : id2
                text : 'Demande'
                size_hint_x : 2

            Button:
                text:'OK'
                background_color : 0.2,0.3,0.7,0.1
                on_release: root.change_label_text()

        BoxLayout:
            orientation : "vertical"
            canvas.before:
                BorderImage:
                    border: 10, 10, 10, 10
                    source: 'Images\BackgroundImage.png'
                    pos: self.pos
                    size: self.size
            FloatLayout:

                size_hint_y : .8
                Label:
                    text : "[size=30]Année[/size]"
                    id : label1
                    color : 0,0,0,1
                    markup : True
                    italic : True
                    pos : (-200,20)

                Label:
                    text : "[size=30]Demande[/size]"
                    id : label2
                    color : 0,0,0,1
                    markup : True
                    italic : True
                    pos : (200,20)

            BoxLayout:
                pos : (0,470)
                size_hint_y : .2
                Button:
                    text: "Main Menu"
                    background_color : 0.2,0.3,0.7,0.7
                    on_release:
                        app.root.current = 'main'
                Button:
                    text: "Show Graph"
                    background_color : 0.2,0.3,0.7,0.7
                    on_release:
                        root.load_list()

<LoadDialog>:
    name : "first"
    BoxLayout:

        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserIconView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: app.root.current = 'main'
            Button:
                text: "Load"
                on_release: root.load_list(filechooser.path, filechooser.selection)
                on_release : app.root.current = 'graphwindow'
<GraphWindow>:
    name : "graphwindow"
    donnees : donnee


    BoxLayout:
        canvas.before:
            BorderImage:
                border: 50, 50, 50, 50
                source: r"3D SMART FACTORY.png"
                pos: self.pos
                size: self.size
        padding : 5
        Button:
            text : "show"
            id : donnee
            size_hint_y : 0.3
            pos_hint: {'x': .3, 'y': .3}
            on_release : root.Show()
""" )

TestApp().run()
