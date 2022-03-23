""" Modified code from Peter Colling Ridge 
	Original found at http://www.petercollingridge.co.uk/pygame-3d-graphics-tutorial
"""

import pygame, math
import numpy as np
import wireframe as wf
import basicShapes as shape

class WireframeViewer(wf.WireframeGroup):
    """ A group of wireframes which can be displayed on a Pygame screen """
    
    def __init__(self, width, height, name="Wireframe Viewer"):
        self.width = width
        self.height = height
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        
        self.wireframes = {}
        self.wireframe_colours = {}
        self.object_to_update = []
        
        self.displayNodes = False
        self.displayEdges = True
        self.displayFaces = True
        
        self.perspective = False
        self.eyeX = self.width/2
        self.eyeY = 100
        self.light_color = np.array([1,1,1])
        self.view_vector = np.array([0, 0, -1])        
        self.light_vector = np.array([0, 0, -1])

        self.background = (10,10,50)
        self.nodeColour = (250,250,250)
        self.nodeRadius = 4

        self.x_rotate = 0.0
        self.y_rotate = 0.0
        self.z_rotate = 0.0
        
        self.control = 0
    
    def addWireframe(self, name, wireframe):
        self.wireframes[name] = wireframe
        #   If colour is set to None, then wireframe is not displayed
        self.wireframe_colours[name] = (250,250,250)
    
    def addWireframeGroup(self, wireframe_group):
        # Potential danger of overwriting names
        for name, wireframe in wireframe_group.wireframes.items():
            self.addWireframe(name, wireframe)
    
    def display(self):
        self.screen.fill(self.background)

        for name, wireframe in self.wireframes.items():
            nodes = wireframe.nodes
            
            if self.displayFaces:
                for (face, colour) in wireframe.sortedFaces():
                    v1 = (nodes[face[1]] - nodes[face[0]])[:3]
                    v2 = (nodes[face[2]] - nodes[face[0]])[:3]

                    normal = np.cross(v1, v2)
                    normal /= np.linalg.norm(normal)
                    towards_us = np.dot(normal, self.view_vector)

                    # Only draw faces that face us
                    if towards_us > 0:
                        m_ambient = 0.1
                        ambient = self.light_color * (m_ambient * colour)
                        not_in_shadow = np.dot(normal, self.light_vector) >= 0.0

                        light_total = ambient

                        if not_in_shadow:
                            k_gls = 5

                            #calculate diffuse
                            k_d = 0.2
                            point_brightness = np.dot(normal, self.light_vector) # (N*L)
                            light_x_colour = np.array([self.light_color[0]*colour[0],self.light_color[1]*colour[1],self.light_color[2]*colour[2]])
                            diffuse = k_d * light_x_colour * point_brightness
                            for i in range(0, 3):
                                if diffuse[i] < 0:
                                    diffuse[i] = 0
                                elif diffuse[i] > 255:
                                    diffuse[i] = 255

                            #calculate specular
                            k_s = 0.7
                            r = normal * (2*point_brightness) - self.light_vector
                            specular = k_s * light_x_colour * pow(np.dot(self.view_vector,r),k_gls)
                            for i in range(0, 3):
                                if specular[i] < 0:
                                    specular[i] = 0
                                elif specular[i] > 255:
                                    specular[i] = 255

                            # Once you have implemented diffuse and specular lighting, you will want to include them here
                            light_total += diffuse + specular

                        #Clip negative vals to 0 and vals>255 to 255
                        for i in range(0,3):
                            if light_total[i] < 0:
                                light_total[i] = 0
                            elif light_total[i] > 255:
                                light_total[i] = 255

                        #If no negative vals in light_total
                        if np.min(light_total) >= 0:
                            try:
                                pygame.draw.polygon(self.screen, (light_total[0],light_total[1],light_total[2]), [(nodes[node][0], nodes[node][1]) for node in face], 0)
                            except ValueError:
                                print(light_total)

                if self.displayEdges:
                    for (n1, n2) in wireframe.edges:
                        if self.perspective:
                            if wireframe.nodes[n1][2] > -self.perspective and nodes[n2][2] > -self.perspective:
                                z1 = self.perspective/ (self.perspective + nodes[n1][2])
                                x1 = self.width/2  + z1*(nodes[n1][0] - self.width/2)
                                y1 = self.height/2 + z1*(nodes[n1][1] - self.height/2)
                    
                                z2 = self.perspective/ (self.perspective + nodes[n2][2])
                                x2 = self.width/2  + z2*(nodes[n2][0] - self.width/2)
                                y2 = self.height/2 + z2*(nodes[n2][1] - self.height/2)
                                
                                pygame.draw.aaline(self.screen, colour, (x1, y1), (x2, y2), 1)
                        else:
                            pygame.draw.aaline(self.screen, colour, (nodes[n1][0], nodes[n1][1]), (nodes[n2][0], nodes[n2][1]), 1)

            if self.displayNodes:
                for node in nodes:
                    pygame.draw.circle(self.screen, colour, (int(node[0]), int(node[1])), self.nodeRadius, 0)
        
        pygame.display.flip()

    def keyEvent(self, key):
        
        #Your code here
        if key == pygame.K_w:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[1,0,0,0],
                                          [0, math.cos(math.pi/20.0), -math.sin(math.pi/20.0), 0],
                                          [0, math.sin(math.pi/20.0), math.cos(math.pi/20.0), 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        if key == pygame.K_s:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[1, 0, 0, 0],
                                          [0, math.cos(math.pi / 20.0), math.sin(math.pi / 20.0), 0],
                                          [0, -math.sin(math.pi / 20.0), math.cos(math.pi / 20.0), 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        if key == pygame.K_a:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[math.cos(math.pi / 20.0), 0, -math.sin(math.pi / 20.0), 0],
                                          [0, 1, 0, 0],
                                          [math.sin(math.pi / 20.0), 0, math.cos(math.pi / 20.0), 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        if key == pygame.K_d:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[math.cos(math.pi / 20.0), 0, math.sin(math.pi / 20.0), 0],
                                          [0, 1, 0, 0],
                                          [-math.sin(math.pi / 20.0), 0, math.cos(math.pi / 20.0), 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        if key == pygame.K_q:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[math.cos(math.pi / 20.0), -math.sin(math.pi / 20.0), 0, 0],
                                          [math.sin(math.pi / 20.0), math.cos(math.pi / 20.0), 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        if key == pygame.K_e:
            light_4 = np.array([self.light_vector[0], self.light_vector[1], self.light_vector[2], 1])
            rotated = light_4 @ np.array([[math.cos(math.pi / 20.0), math.sin(math.pi / 20.0), 0, 0],
                                          [-math.sin(math.pi / 20.0), math.cos(math.pi / 20.0), 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
            self.light_vector = np.array([rotated[0], rotated[1], rotated[2]])

        return

    def run(self):
        """ Display wireframe on screen and respond to keydown events """
        
        running = True
        key_down = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    key_down = event.key
                elif event.type == pygame.KEYUP:
                    key_down = None
            
            if key_down:
                self.keyEvent(key_down)
            
            self.display()
            self.update()
            
        pygame.quit()

		
resolution = 52
viewer = WireframeViewer(600, 400)
viewer.addWireframe('sphere', shape.Spheroid((300,200, 20), (160,160,160), resolution=resolution))

# Colour ball
faces = viewer.wireframes['sphere'].faces
for i in range(int(resolution/4)):
	for j in range(resolution*2-4):
		f = i*(resolution*4-8) +j
		faces[f][1][1] = 0
		faces[f][1][2] = 0
	
viewer.displayEdges = False
viewer.run()
