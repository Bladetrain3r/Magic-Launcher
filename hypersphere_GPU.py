import math
import sys
import os
import json
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
import ctypes
import time

class GPU4DHypersphereViewer:
    def __init__(self):
        # Hypersphere parameters
        self.point_count = 5000
        self.distribution = 'fibonacci'  # 'fibonacci', 'grid', 'shell', or 'random'
        self.shell_count = 20  # For shell distribution
        
        # 4D rotation angles and position
        self.w_angle = 0.0
        self.w_position = 0.0
        self.xw_rotation_speed = 0.5
        self.yz_rotation_speed = 0.3
        self.zw_rotation_speed = 0.2
        self.xy_rotation_speed = 0.4
        self.auto_rotate_4d = False
        
        # 3D camera settings
        self.camera_pos = [0, 0, 4]
        self.rotation = [0, 0, 0]
        self.auto_rotate_3d = False
        self.auto_rotate_speed = [0.5, 0.5]
        
        # Display settings
        self.width = 1280
        self.height = 1280
        self.base_point_size = 2.0
        self.color_mode = 0  # 0: w-coordinate, 1: radial, 2: angle-based
        
        # Beat detection (simplified for real-time)
        self.beat_active = False
        self.beat_intensity = 0.0
        self.zoom_factor = 2.0
        
        # OpenGL objects
        self.shader_program = None
        self.vao = None
        self.vbo = None
        self.vertex_count = 0

    def initialize_pygame_and_opengl(self):
        """Initialize Pygame and create OpenGL context"""
        pygame.init()
        
        # Set OpenGL attributes
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        
        # Create window
        display = (self.width, self.height)
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("GPU 4D Hypersphere Viewer")
        
        # Force context creation
        pygame.display.flip()
        time.sleep(0.1)
        
        # Verify context
        try:
            version = glGetString(GL_VERSION)
            if version:
                print(f"OpenGL Version: {version.decode()}")
                print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
                print(f"Renderer: {glGetString(GL_RENDERER).decode()}")
            else:
                raise Exception("Failed to get OpenGL version")
        except Exception as e:
            print(f"OpenGL context verification failed: {e}")
            raise

    def create_shaders(self):
        """Create vertex and fragment shaders for 4D hypersphere rendering"""
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in float index;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time;
        uniform float point_count;
        uniform int distribution_type;
        uniform int shell_count;
        uniform float w_angle;
        uniform float w_position;
        uniform float xw_speed;
        uniform float yz_speed;
        uniform float zw_speed;
        uniform float xy_speed;
        uniform float base_point_size;
        uniform float zoom_factor;
        uniform float beat_intensity;
        
        out vec3 FragPos;
        out vec4 SphereCoord4D;
        out float WCoord;
        out float RadialDist;
        
        const float PI = 3.14159265359;
        const float golden_ratio = 2.618033988749895;  // (1 + sqrt(5)) / 2 * 1.618...
        
        vec4 generate_hypersphere_point(float idx) {
            vec4 point4d;
            
            if (distribution_type == 0) {  // Fibonacci
                // Fibonacci spiral distribution on 4D hypersphere
                float phi = 2.0 * PI * mod(idx / golden_ratio, 1.0);
                float cos_theta = 2.0 * (idx / point_count) - 1.0;
                float theta = acos(cos_theta);
                float psi = phi * golden_ratio;
                
                float sin_theta = sin(theta);
                
                point4d.x = sin_theta * cos(phi) * sin(psi);
                point4d.y = sin_theta * sin(phi) * sin(psi);
                point4d.z = sin_theta * cos(psi);
                point4d.w = cos_theta;
                
            } else if (distribution_type == 1) {  // Grid
                // Evenly spaced grid distribution
                float grid_size = pow(point_count, 0.25);
                float i1 = mod(idx, grid_size);
                float i2 = mod(floor(idx / grid_size), grid_size);
                float i3 = mod(floor(idx / (grid_size * grid_size)), grid_size);
                
                float u = i1 / grid_size * 2.0 * PI;
                float v = i2 / grid_size * PI;
                float w = i3 / grid_size * PI;
                
                float sin_u = sin(u), cos_u = cos(u);
                float sin_v = sin(v), cos_v = cos(v);
                float sin_w = sin(w), cos_w = cos(w);
                
                point4d.x = sin_u * sin_v * sin_w;
                point4d.y = sin_u * sin_v * cos_w;
                point4d.z = sin_u * cos_v;
                point4d.w = cos_u;
                
            } else if (distribution_type == 2) {  // Shell
                // Concentric shells
                float shell_idx = mod(idx, float(shell_count));
                float point_in_shell = floor(idx / float(shell_count));
                float points_per_shell = point_count / float(shell_count);
                
                // Use fibonacci on each shell
                float t = point_in_shell / points_per_shell;
                float phi = 2.0 * PI * mod(point_in_shell / golden_ratio, 1.0);
                float theta = acos(2.0 * t - 1.0);
                float psi = phi * golden_ratio;
                
                // Add shell offset
                float shell_offset = shell_idx * PI / float(shell_count);
                phi += shell_offset;
                psi += shell_offset * 2.0;
                
                float sin_theta = sin(theta);
                
                point4d.x = sin_theta * cos(phi) * sin(psi);
                point4d.y = sin_theta * sin(phi) * sin(psi);
                point4d.z = sin_theta * cos(psi);
                point4d.w = cos(theta);
                
            } else {  // Random
                // Pseudo-random based on index
                float u = fract(sin(idx * 12.9898) * 43758.5453) * 2.0 * PI;
                float v = fract(sin(idx * 78.233) * 43758.5453) * PI;
                float w = fract(sin(idx * 45.164) * 43758.5453) * PI;
                
                float sin_u = sin(u), cos_u = cos(u);
                float sin_v = sin(v), cos_v = cos(v);
                float sin_w = sin(w), cos_w = cos(w);
                
                point4d.x = sin_u * sin_v * sin_w;
                point4d.y = sin_u * sin_v * cos_w;
                point4d.z = sin_u * cos_v;
                point4d.w = cos_u;
            }
            
            return point4d;
        }
        
        vec3 project_4d_to_3d(vec4 point4d) {
            // Apply 4D rotations
            float total_angle = w_angle;
            if (time > 0.0) {
                total_angle += time * 0.001;
            }
            
            // XW rotation
            float cos_xw = cos(total_angle * xw_speed);
            float sin_xw = sin(total_angle * xw_speed);
            float new_x = point4d.x * cos_xw - point4d.w * sin_xw;
            float new_w = point4d.x * sin_xw + point4d.w * cos_xw;
            point4d.x = new_x;
            point4d.w = new_w;
            
            // YZ rotation
            float cos_yz = cos(total_angle * yz_speed * 0.5);
            float sin_yz = sin(total_angle * yz_speed * 0.5);
            float new_y = point4d.y * cos_yz - point4d.z * sin_yz;
            float new_z = point4d.y * sin_yz + point4d.z * cos_yz;
            point4d.y = new_y;
            point4d.z = new_z;
            
            // ZW rotation
            float cos_zw = cos(total_angle * zw_speed * 0.3);
            float sin_zw = sin(total_angle * zw_speed * 0.3);
            new_z = point4d.z * cos_zw - point4d.w * sin_zw;
            new_w = point4d.z * sin_zw + point4d.w * cos_zw;
            point4d.z = new_z;
            point4d.w = new_w;
            
            // XY rotation for additional movement
            float cos_xy = cos(total_angle * xy_speed * 0.7);
            float sin_xy = sin(total_angle * xy_speed * 0.7);
            new_x = point4d.x * cos_xy - point4d.y * sin_xy;
            new_y = point4d.x * sin_xy + point4d.y * cos_xy;
            point4d.x = new_x;
            point4d.y = new_y;
            
            // Apply W-axis translation
            point4d.w += w_position;
            
            // Store W coordinate for coloring
            WCoord = point4d.w;
            
            // Calculate radial distance for effects
            RadialDist = length(point4d);
            
            // Apply zoom with beat intensity
            float dynamic_zoom = zoom_factor + beat_intensity * 2.0;
            
            // Stereographic projection from 4D to 3D
            float projection_factor = 1.25 / (1.0 - point4d.w * 0.15);
            projection_factor *= dynamic_zoom * 0.5;
            
            vec3 point3d;
            point3d.x = point4d.x * projection_factor;
            point3d.y = point4d.y * projection_factor;
            point3d.z = point4d.z * projection_factor;
            
            return point3d;
        }
        
        void main()
        {
            // Generate 4D hypersphere point
            vec4 point4d = generate_hypersphere_point(index);
            SphereCoord4D = point4d;
            
            // Project to 3D
            vec3 pos = project_4d_to_3d(point4d);
            FragPos = pos;
            
            // Apply transformations
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Dynamic point size with beat and W coordinate
            float w_influence = (WCoord + 1.0) * 0.5;
            gl_PointSize = base_point_size * (1.0 + w_influence + beat_intensity);
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec4 SphereCoord4D;
        in float WCoord;
        in float RadialDist;
        
        uniform int color_mode;
        uniform float time;
        uniform float beat_intensity;
        uniform vec3 color_low;
        uniform vec3 color_high;
        
        out vec4 FragColor;
        
        vec3 hsv_to_rgb(vec3 hsv) {
            float h = hsv.x;
            float s = hsv.y;
            float v = hsv.z;
            
            float c = v * s;
            float x = c * (1.0 - abs(mod(h / 60.0, 2.0) - 1.0));
            float m = v - c;
            
            vec3 rgb;
            if (h < 60.0) rgb = vec3(c, x, 0.0);
            else if (h < 120.0) rgb = vec3(x, c, 0.0);
            else if (h < 180.0) rgb = vec3(0.0, c, x);
            else if (h < 240.0) rgb = vec3(0.0, x, c);
            else if (h < 300.0) rgb = vec3(x, 0.0, c);
            else rgb = vec3(c, 0.0, x);
            
            return rgb + m;
        }
        
        void main()
        {
            vec3 color;
            
            if (color_mode == 0) {  // W-coordinate gradient
                float t = (WCoord + 1.0) * 0.5;
                
                // Apply beat intensity to color interpolation
                t = mix(t, 1.0 - t, beat_intensity * 0.5);
                
                // Interpolate between colors
                color = mix(color_low, color_high, t);
                
            } else if (color_mode == 1) {  // Radial rainbow
                float hue = RadialDist * 180.0 + time * 0.02;
                float saturation = 0.8 + beat_intensity * 0.2;
                float value = 0.7 + 0.3 * sin(RadialDist * 10.0 + time * 0.001);
                color = hsv_to_rgb(vec3(mod(hue, 360.0), saturation, value));
                
            } else {  // Angle-based psychedelic
                float angle1 = atan(SphereCoord4D.y, SphereCoord4D.x);
                float angle2 = atan(SphereCoord4D.w, SphereCoord4D.z);
                float combined = angle1 + angle2 + time * 0.001;
                
                float hue = combined * 57.2958 + beat_intensity * 60.0;
                float saturation = 0.9;
                float value = 0.6 + 0.4 * (WCoord + 1.0) * 0.5;
                color = hsv_to_rgb(vec3(mod(hue, 360.0), saturation, value));
            }
            
            // Add glow effect based on beat
            color += vec3(beat_intensity * 0.2);
            
            // Depth shading
            float depth = gl_FragCoord.z;
            color *= (1.2 - depth * 0.2);
            
            FragColor = vec4(color, 1.0);
        }
        """
        
        try:
            # Compile shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            print("4D Hypersphere GPU shaders compiled successfully!")
        except Exception as e:
            print(f"Shader compilation error: {e}")
            raise

    def create_vertex_buffer(self):
        """Create vertex buffer with point indices"""
        # Create array of indices
        indices = np.arange(self.point_count, dtype=np.float32)
        
        # Create VAO and VBO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        # Set vertex attributes
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glBindVertexArray(0)
        
        self.vertex_count = len(indices)
        print(f"Created vertex buffer with {self.vertex_count} points")

    def init_gl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Enable point size control from shaders
        glEnable(GL_PROGRAM_POINT_SIZE)
        
        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Create shaders and vertex buffer
        self.create_shaders()
        self.create_vertex_buffer()
        
        print("GPU initialization complete")

    def get_projection_matrix(self):
        """Get perspective projection matrix"""
        fov = 45.0
        aspect = self.width / self.height
        near = 0.1
        far = 50.0
        
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        matrix = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        
        return matrix

    def get_view_matrix(self):
        """Get view matrix from camera position and rotation"""
        # Create translation matrix
        translation = np.eye(4, dtype=np.float32)
        translation[0, 3] = -self.camera_pos[0]
        translation[1, 3] = -self.camera_pos[1]
        translation[2, 3] = -self.camera_pos[2]
        
        # Create rotation matrices
        rx = math.radians(self.rotation[0])
        ry = math.radians(self.rotation[1])
        rz = math.radians(self.rotation[2])
        
        # X rotation
        rot_x = np.eye(4, dtype=np.float32)
        rot_x[1, 1] = math.cos(rx)
        rot_x[1, 2] = -math.sin(rx)
        rot_x[2, 1] = math.sin(rx)
        rot_x[2, 2] = math.cos(rx)
        
        # Y rotation
        rot_y = np.eye(4, dtype=np.float32)
        rot_y[0, 0] = math.cos(ry)
        rot_y[0, 2] = math.sin(ry)
        rot_y[2, 0] = -math.sin(ry)
        rot_y[2, 2] = math.cos(ry)
        
        # Z rotation
        rot_z = np.eye(4, dtype=np.float32)
        rot_z[0, 0] = math.cos(rz)
        rot_z[0, 1] = -math.sin(rz)
        rot_z[1, 0] = math.sin(rz)
        rot_z[1, 1] = math.cos(rz)
        
        # Combine transformations
        view = translation @ rot_x @ rot_y @ rot_z
        return view

    def display(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Use shader program
        glUseProgram(self.shader_program)
        
        # Get current time for animations
        current_time = pygame.time.get_ticks() if self.auto_rotate_4d else 0
        
        # Update beat intensity (decay over time)
        self.beat_intensity *= 0.95
        
        # Set uniforms
        uniforms = {
            'projection': glGetUniformLocation(self.shader_program, "projection"),
            'view': glGetUniformLocation(self.shader_program, "view"),
            'model': glGetUniformLocation(self.shader_program, "model"),
            'time': glGetUniformLocation(self.shader_program, "time"),
            'point_count': glGetUniformLocation(self.shader_program, "point_count"),
            'distribution_type': glGetUniformLocation(self.shader_program, "distribution_type"),
            'shell_count': glGetUniformLocation(self.shader_program, "shell_count"),
            'w_angle': glGetUniformLocation(self.shader_program, "w_angle"),
            'w_position': glGetUniformLocation(self.shader_program, "w_position"),
            'xw_speed': glGetUniformLocation(self.shader_program, "xw_speed"),
            'yz_speed': glGetUniformLocation(self.shader_program, "yz_speed"),
            'zw_speed': glGetUniformLocation(self.shader_program, "zw_speed"),
            'xy_speed': glGetUniformLocation(self.shader_program, "xy_speed"),
            'base_point_size': glGetUniformLocation(self.shader_program, "base_point_size"),
            'zoom_factor': glGetUniformLocation(self.shader_program, "zoom_factor"),
            'beat_intensity': glGetUniformLocation(self.shader_program, "beat_intensity"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode"),
            'color_low': glGetUniformLocation(self.shader_program, "color_low"),
            'color_high': glGetUniformLocation(self.shader_program, "color_high")
        }
        
        # Set matrices
        projection = self.get_projection_matrix()
        view = self.get_view_matrix()
        model = np.eye(4, dtype=np.float32)
        
        glUniformMatrix4fv(uniforms['projection'], 1, GL_TRUE, projection)
        glUniformMatrix4fv(uniforms['view'], 1, GL_TRUE, view)
        glUniformMatrix4fv(uniforms['model'], 1, GL_TRUE, model)
        
        # Set other uniforms
        glUniform1f(uniforms['time'], current_time)
        glUniform1f(uniforms['point_count'], self.point_count)
        
        # Distribution type: 0=fibonacci, 1=grid, 2=shell, 3=random
        dist_map = {'fibonacci': 0, 'grid': 1, 'shell': 2, 'random': 3}
        glUniform1i(uniforms['distribution_type'], dist_map.get(self.distribution, 0))
        glUniform1i(uniforms['shell_count'], self.shell_count)
        
        glUniform1f(uniforms['w_angle'], self.w_angle)
        glUniform1f(uniforms['w_position'], self.w_position)
        glUniform1f(uniforms['xw_speed'], self.xw_rotation_speed)
        glUniform1f(uniforms['yz_speed'], self.yz_rotation_speed)
        glUniform1f(uniforms['zw_speed'], self.zw_rotation_speed)
        glUniform1f(uniforms['xy_speed'], self.xy_rotation_speed)
        glUniform1f(uniforms['base_point_size'], self.base_point_size)
        glUniform1f(uniforms['zoom_factor'], self.zoom_factor)
        glUniform1f(uniforms['beat_intensity'], self.beat_intensity)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        
        # Set colors (normalized to 0-1)
        color_low = [0.0, 0.0, 1.0]  # Blue
        color_high = [1.0, 0.0, 0.0]  # Red
        glUniform3f(uniforms['color_low'], *color_low)
        glUniform3f(uniforms['color_high'], *color_high)
        
        # Draw
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)
        
        pygame.display.flip()

    def run(self):
        """Main loop"""
        # Initialize
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nGPU 4D Hypersphere Viewer")
        print("\nControls:")
        print("  Arrow keys: Rotate 3D view")
        print("  Page Up/Down: Zoom in/out")
        print("  W/S: Rotate in 4D (W dimension)")
        print("  T/G: Pan along W axis (4th dimension)")
        print("  Q/E: Decrease/Increase point size")
        print("  A: Toggle 3D auto-rotation")
        print("  D: Toggle 4D auto-rotation")
        print("  C: Cycle color modes")
        print("  F: Cycle distribution (fibonacci/grid/shell/random)")
        print("  B: Simulate beat (for testing)")
        print("  +/-: Adjust zoom factor")
        print("  1/2/3/4: Adjust 4D rotation speeds")
        print("  R: Reset view")
        print("  ESC: Quit")
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reset view
                        self.camera_pos = [0, 0, -3]
                        self.rotation = [0, 0, 0]
                        self.w_angle = 0.0
                        self.w_position = 0.0
                        self.base_point_size = 2.0
                        self.zoom_factor = 2.0
                        print("View reset")
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] += 0.5
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] -= 0.5
                    elif event.key == pygame.K_q:
                        self.base_point_size = max(0.5, self.base_point_size - 0.5)
                        print(f"Point size: {self.base_point_size:.1f}")
                    elif event.key == pygame.K_e:
                        self.base_point_size = min(10.0, self.base_point_size + 0.5)
                        print(f"Point size: {self.base_point_size:.1f}")
                    elif event.key == pygame.K_a:
                        self.auto_rotate_3d = not self.auto_rotate_3d
                        print(f"3D Auto-rotation: {'ON' if self.auto_rotate_3d else 'OFF'}")
                    elif event.key == pygame.K_d:
                        self.auto_rotate_4d = not self.auto_rotate_4d
                        print(f"4D Auto-rotation: {'ON' if self.auto_rotate_4d else 'OFF'}")
                    elif event.key == pygame.K_c:
                        self.color_mode = (self.color_mode + 1) % 3
                        modes = ['W-gradient', 'Radial rainbow', 'Psychedelic']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_f:
                        distributions = ['fibonacci', 'grid', 'shell', 'random']
                        current_idx = distributions.index(self.distribution)
                        self.distribution = distributions[(current_idx + 1) % 4]
                        print(f"Distribution: {self.distribution}")
                    elif event.key == pygame.K_b:
                        # Simulate beat
                        self.beat_intensity = 1.0
                        print("Beat!")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.zoom_factor = min(5.0, self.zoom_factor + 0.2)
                        print(f"Zoom factor: {self.zoom_factor:.1f}")
                    elif event.key == pygame.K_MINUS:
                        self.zoom_factor = max(0.5, self.zoom_factor - 0.2)
                        print(f"Zoom factor: {self.zoom_factor:.1f}")
                    elif event.key == pygame.K_1:
                        self.xw_rotation_speed *= 1.2
                        print(f"XW rotation speed: {self.xw_rotation_speed:.2f}")
                    elif event.key == pygame.K_2:
                        self.yz_rotation_speed *= 1.2
                        print(f"YZ rotation speed: {self.yz_rotation_speed:.2f}")
                    elif event.key == pygame.K_3:
                        self.zw_rotation_speed *= 1.2
                        print(f"ZW rotation speed: {self.zw_rotation_speed:.2f}")
                    elif event.key == pygame.K_4:
                        self.xy_rotation_speed *= 1.2
                        print(f"XY rotation speed: {self.xy_rotation_speed:.2f}")
            
            # Handle continuous rotation and movement
            keys = pygame.key.get_pressed()
            
            if self.auto_rotate_3d:
                self.rotation[0] += self.auto_rotate_speed[0]
                self.rotation[1] += self.auto_rotate_speed[1]
            else:
                if keys[pygame.K_LEFT]:
                    self.rotation[1] -= 2
                if keys[pygame.K_RIGHT]:
                    self.rotation[1] += 2
                if keys[pygame.K_UP]:
                    self.rotation[0] -= 2
                if keys[pygame.K_DOWN]:
                    self.rotation[0] += 2
            
            # Continuous W-dimension controls
            if keys[pygame.K_w]:
                self.w_angle += 0.02
            if keys[pygame.K_s]:
                self.w_angle -= 0.02
            if keys[pygame.K_t]:
                self.w_position += 0.02
            if keys[pygame.K_g]:
                self.w_position -= 0.02
            
            self.display()
            clock.tick(60)
        
        # Cleanup
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        
        pygame.quit()

def main():
    try:
        viewer = GPU4DHypersphereViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Check your graphics drivers are up to date")
        print("3. Try reducing point_count if performance is poor")

if __name__ == "__main__":
    main()