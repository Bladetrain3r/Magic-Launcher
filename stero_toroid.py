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

class GPU4DToroidViewer:
    def __init__(self):
        # Toroid parameters
        self.major_radius = 2.0
        self.minor_radius = 1.0
        self.point_count = 100000
        self.distribution = 'spherical_fibonacci'  # 'spherical_fibonacci', 'grid', or 'random'
        
        # 4D rotation angles and position
        self.w_angle = 0.0
        self.w_position = 0.0  # Position along W axis
        self.xw_rotation_speed = 0.5
        self.yz_rotation_speed = 0.3
        self.zw_rotation_speed = 0.2
        self.auto_rotate_4d = False
        
        # 3D camera settings
        self.camera_pos = [0, 0, 4]
        self.rotation = [0, 0, 0]
        self.auto_rotate_3d = False
        self.auto_rotate_speed = [0.5, 0.5]
        
        # Display settings
        self.width = 1600
        self.height = 900
        self.point_size = 2.0
        self.base_point_size = 2.0  # For point size adjustment
        self.color_mode = 0  # 0: w-coordinate, 1: distance, 2: angle-based
        
        # Stereoscopic settings
        self.stereoscopic_mode = 0  # 0: off, 1: side-by-side, 2: anaglyph (red/cyan)
        self.eye_separation = 0.15  # Distance between eyes
        self.convergence_distance = 4.0  # Where eyes converge
        
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
        pygame.display.set_caption("GPU 4D Toroid Viewer - Stereoscopic")
        
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
        """Create vertex and fragment shaders for 4D toroid rendering"""
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in float index;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time;
        uniform float point_count;
        uniform float major_radius;
        uniform float minor_radius;
        uniform int distribution_type;
        uniform float w_angle;
        uniform float xw_speed;
        uniform float yz_speed;
        uniform float zw_speed;
        uniform float base_point_size;
        uniform float w_position;
        
        out vec3 FragPos;
        out vec4 ToroidCoord4D;
        out float WCoord;
        
        const float PI = 3.14159265359;
        const float PHI = 1.618033988749895;  // Golden ratio
        
        vec4 generate_toroid_point(float idx) {
            vec4 point4d;
            
            if (distribution_type == 0) {  // Spherical Fibonacci
                // Spherical fibonacci lattice on 4D hypersphere
                float n = point_count;
                float i = idx + 0.5;
                
                // Generate angles using golden angle in multiple dimensions
                float theta = acos(1.0 - 2.0 * i / n);  // Latitude
                float phi = 2.0 * PI * i / PHI;  // Longitude
                
                // Additional angles for 4D
                float psi = 2.0 * PI * fract(i * PHI);
                float chi = 2.0 * PI * fract(i * PHI * PHI);
                
                // Map to toroid surface in 4D
                float r_major = major_radius;
                float r_minor = minor_radius;
                
                // Create toroidal coordinates
                float u = theta;
                float v = phi;
                float w = psi;
                
                // Generate 4D toroid point
                float r = r_major + r_minor * cos(w);
                point4d.x = r * cos(u) * cos(v);
                point4d.y = r * sin(u) * cos(v);
                point4d.z = r * sin(v);
                point4d.w = r_minor * sin(w);
                
            } else if (distribution_type == 1) {  // Grid
                // Decompose index into 4 dimensions
                float points_per_dim = pow(point_count, 0.25);
                float i1 = mod(idx, points_per_dim);
                float i2 = mod(floor(idx / points_per_dim), points_per_dim);
                float i3 = mod(floor(idx / (points_per_dim * points_per_dim)), points_per_dim);
                float i4 = floor(idx / (points_per_dim * points_per_dim * points_per_dim));
                
                float theta1 = 2.0 * PI * i1 / points_per_dim;
                float theta2 = 2.0 * PI * i2 / points_per_dim;
                float theta3 = 2.0 * PI * i3 / points_per_dim;
                float theta4 = 2.0 * PI * i4 / points_per_dim;
                
                float r1 = major_radius + minor_radius * cos(theta3);
                point4d.x = r1 * cos(theta1);
                point4d.y = r1 * sin(theta1);
                
                float r2 = major_radius + minor_radius * sin(theta3);
                point4d.z = r2 * cos(theta2);
                point4d.w = r2 * sin(theta2);
                
            } else {  // Random (pseudo-random based on index)
                // Use index-based pseudo-random for consistency
                float theta1 = fract(sin(idx * 12.9898) * 43758.5453) * 2.0 * PI;
                float theta2 = fract(sin(idx * 78.233) * 43758.5453) * 2.0 * PI;
                float theta3 = fract(sin(idx * 45.164) * 43758.5453) * 2.0 * PI;
                float theta4 = fract(sin(idx * 94.673) * 43758.5453) * 2.0 * PI;
                
                float r1 = major_radius + minor_radius * cos(theta3);
                point4d.x = r1 * cos(theta1);
                point4d.y = r1 * sin(theta1);
                
                float r2 = major_radius + minor_radius * sin(theta3);
                point4d.z = r2 * cos(theta2);
                point4d.w = r2 * sin(theta2);
            }
            
            // Normalize
            float max_val = max(max(abs(point4d.x), abs(point4d.y)), max(abs(point4d.z), abs(point4d.w)));
            if (max_val > 0.0) point4d /= max_val;
            
            return point4d;
        }
        
        vec3 project_4d_to_3d(vec4 point4d) {
            // Apply 4D rotations
            float total_angle = w_angle;
            if (time > 0.0) {  // Only add time-based rotation if time is being passed
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
            
            // ZW rotation for extra dimensionality
            float cos_zw = cos(total_angle * zw_speed * 0.3);
            float sin_zw = sin(total_angle * zw_speed * 0.3);
            new_z = point4d.z * cos_zw - point4d.w * sin_zw;
            new_w = point4d.z * sin_zw + point4d.w * cos_zw;
            point4d.z = new_z;
            point4d.w = new_w;
            
            // Apply W-axis translation after rotations
            point4d.w += w_position;
            
            // Store final W coordinate for coloring
            WCoord = point4d.w;
            
            // Project to 3D using stereographic projection
            float projection_factor = 1.25 / (1.0 - point4d.w * 0.2);
            vec3 point3d;
            point3d.x = point4d.x * projection_factor;
            point3d.y = point4d.y * projection_factor;
            point3d.z = point4d.z * projection_factor;
            
            return point3d;
        }
        
        void main()
        {
            // Generate 4D toroid point
            vec4 point4d = generate_toroid_point(index);
            ToroidCoord4D = point4d;
            
            // Project to 3D
            vec3 pos = project_4d_to_3d(point4d);
            FragPos = pos;
            
            // Apply transformations
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Dynamic point size based on W coordinate and base size
            gl_PointSize = base_point_size + base_point_size * (WCoord + 1.0) * 0.5;
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec4 ToroidCoord4D;
        in float WCoord;
        
        uniform int color_mode;
        uniform float time;
        
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
            
            if (color_mode == 0) {  // W-coordinate based
                // Map W coordinate to hue
                float hue = (WCoord + 1.0) * 180.0;  // 0-360 degrees
                float saturation = 0.8;
                float value = 0.9;
                color = hsv_to_rgb(vec3(hue, saturation, value));
                
            } else if (color_mode == 1) {  // Distance-based
                float dist = length(ToroidCoord4D);
                float hue = dist * 120.0;
                float saturation = 0.7;
                float value = 0.8 + 0.2 * sin(dist * 5.0);
                color = hsv_to_rgb(vec3(mod(hue, 360.0), saturation, value));
                
            } else {  // Angle-based
                float angle = atan(ToroidCoord4D.y, ToroidCoord4D.x) + 3.14159;
                float angle2 = atan(ToroidCoord4D.w, ToroidCoord4D.z) + 3.14159;
                float hue = (angle + angle2) * 57.2958;  // Convert to degrees
                float saturation = 0.9;
                float value = 0.8 + 0.2 * (WCoord + 1.0) * 0.5;
                color = hsv_to_rgb(vec3(hue, saturation, value));
            }
            
            // Add some depth shading
            float depth = gl_FragCoord.z;
            color *= (1.3 - depth * 0.3);
            
            FragColor = vec4(color, 1.0);
        }
        """
        
        try:
            # Compile shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            print("4D Toroid GPU shaders compiled successfully!")
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
        glClearColor(0.02, 0.02, 0.05, 1.0)  # Dark background
        
        # Enable point size control from shaders
        glEnable(GL_PROGRAM_POINT_SIZE)
        
        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Create shaders and vertex buffer
        self.create_shaders()
        self.create_vertex_buffer()
        
        print("GPU initialization complete")

    def get_projection_matrix_stereo(self, width, height, eye_offset):
        """Get perspective projection matrix with stereo offset"""
        fov = 45.0
        aspect = width / height
        near = 0.1
        far = 100.0
        
        # Calculate frustum parameters
        top = near * math.tan(math.radians(fov) / 2.0)
        bottom = -top
        
        # Adjust for stereo with toe-in
        frustum_shift = -(eye_offset * near) / self.convergence_distance
        left = -aspect * top + frustum_shift
        right = aspect * top + frustum_shift
        
        # Create frustum matrix
        matrix = np.zeros((4, 4), dtype=np.float32)
        matrix[0, 0] = (2.0 * near) / (right - left)
        matrix[1, 1] = (2.0 * near) / (top - bottom)
        matrix[0, 2] = (right + left) / (right - left)
        matrix[1, 2] = (top + bottom) / (top - bottom)
        matrix[2, 2] = -(far + near) / (far - near)
        matrix[2, 3] = -(2.0 * far * near) / (far - near)
        matrix[3, 2] = -1.0
        
        return matrix

    def get_projection_matrix(self):
        """Get perspective projection matrix (non-stereo)"""
        return self.get_projection_matrix_stereo(self.width, self.height, 0.0)

    def get_view_matrix_stereo(self, eye_offset):
        """Get view matrix with stereo eye offset"""
        # Create translation matrix with eye offset
        translation = np.eye(4, dtype=np.float32)
        translation[0, 3] = -(self.camera_pos[0] + eye_offset)
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

    def get_view_matrix(self):
        """Get view matrix from camera position and rotation (non-stereo)"""
        return self.get_view_matrix_stereo(0.0)

    def render_eye(self, x, y, width, height, eye_offset):
        """Render from a single eye perspective"""
        # Use shader program
        glUseProgram(self.shader_program)
        
        # Get current time for animations
        current_time = pygame.time.get_ticks() if self.auto_rotate_4d else 0
        
        # Set uniforms
        uniforms = {
            'projection': glGetUniformLocation(self.shader_program, "projection"),
            'view': glGetUniformLocation(self.shader_program, "view"),
            'model': glGetUniformLocation(self.shader_program, "model"),
            'time': glGetUniformLocation(self.shader_program, "time"),
            'point_count': glGetUniformLocation(self.shader_program, "point_count"),
            'major_radius': glGetUniformLocation(self.shader_program, "major_radius"),
            'minor_radius': glGetUniformLocation(self.shader_program, "minor_radius"),
            'distribution_type': glGetUniformLocation(self.shader_program, "distribution_type"),
            'w_angle': glGetUniformLocation(self.shader_program, "w_angle"),
            'xw_speed': glGetUniformLocation(self.shader_program, "xw_speed"),
            'yz_speed': glGetUniformLocation(self.shader_program, "yz_speed"),
            'zw_speed': glGetUniformLocation(self.shader_program, "zw_speed"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode"),
            'w_position': glGetUniformLocation(self.shader_program, "w_position"),
            'base_point_size': glGetUniformLocation(self.shader_program, "base_point_size")
        }
        
        # Set matrices
        projection = self.get_projection_matrix_stereo(width, height, eye_offset)
        view = self.get_view_matrix_stereo(eye_offset)
        model = np.eye(4, dtype=np.float32)
        
        glUniformMatrix4fv(uniforms['projection'], 1, GL_TRUE, projection)
        glUniformMatrix4fv(uniforms['view'], 1, GL_TRUE, view)
        glUniformMatrix4fv(uniforms['model'], 1, GL_TRUE, model)
        
        # Set other uniforms
        glUniform1f(uniforms['time'], current_time)
        glUniform1f(uniforms['point_count'], self.point_count)
        glUniform1f(uniforms['major_radius'], self.major_radius)
        glUniform1f(uniforms['minor_radius'], self.minor_radius)
        
        # Distribution type: 0=spherical_fibonacci, 1=grid, 2=random
        dist_map = {'spherical_fibonacci': 0, 'grid': 1, 'random': 2}
        glUniform1i(uniforms['distribution_type'], dist_map.get(self.distribution, 0))
        
        glUniform1f(uniforms['w_angle'], self.w_angle)
        glUniform1f(uniforms['xw_speed'], self.xw_rotation_speed)
        glUniform1f(uniforms['yz_speed'], self.yz_rotation_speed)
        glUniform1f(uniforms['zw_speed'], self.zw_rotation_speed)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        glUniform1f(uniforms['w_position'], self.w_position)
        glUniform1f(uniforms['base_point_size'], self.base_point_size)
        
        # Draw
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)

    def display(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.stereoscopic_mode == 0:
            # Normal rendering
            self.render_eye(0, 0, self.width, self.height, 0.0)
        elif self.stereoscopic_mode == 1:
            # Side-by-side stereoscopic
            # Left eye
            glViewport(0, 0, self.width // 2, self.height)
            self.render_eye(0, 0, self.width // 2, self.height, -self.eye_separation)
            
            # Right eye
            glViewport(self.width // 2, 0, self.width // 2, self.height)
            self.render_eye(self.width // 2, 0, self.width // 2, self.height, self.eye_separation)
            
            # Reset viewport
            glViewport(0, 0, self.width, self.height)
        elif self.stereoscopic_mode == 2:
            # Anaglyph (red/cyan) stereoscopic
            # Left eye (red channel)
            glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
            self.render_eye(0, 0, self.width, self.height, -self.eye_separation)
            
            # Clear depth buffer for second pass
            glClear(GL_DEPTH_BUFFER_BIT)
            
            # Right eye (cyan channels)
            glColorMask(GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE)
            self.render_eye(0, 0, self.width, self.height, self.eye_separation)
            
            # Reset color mask
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        
        pygame.display.flip()

    def run(self):
        """Main loop"""
        # Initialize
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nGPU 4D Toroid Viewer - Stereoscopic Edition")
        print("\nControls:")
        print("  Arrow keys: Rotate 3D view")
        print("  Page Up/Down: Zoom in/out")
        print("  W/S: Rotate in 4D (W dimension)")
        print("  T/G: Pan along W axis (4th dimension)")
        print("  Q/E: Decrease/Increase point size")
        print("  A: Toggle 3D auto-rotation")
        print("  D: Toggle 4D auto-rotation")
        print("  C: Cycle color modes")
        print("  F: Cycle distribution (spherical_fibonacci/grid/random)")
        print("  +/-: Adjust major radius")
        print("  [/]: Adjust minor radius")
        print("  1/2/3: Adjust 4D rotation speeds")
        print("  X: Cycle stereoscopic modes (off/side-by-side/anaglyph)")
        print("  ,/.: Adjust eye separation")
        print("  </> (shifted ,/.): Adjust convergence distance")
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
                        self.camera_pos = [0, 0, 4]
                        self.rotation = [0, 0, 0]
                        self.w_angle = 0.0
                        self.w_position = 0.0
                        self.base_point_size = 2.0
                        self.eye_separation = 0.15
                        self.convergence_distance = 4.0
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
                        modes = ['W-coordinate', 'Distance', 'Angle-based']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_f:
                        distributions = ['spherical_fibonacci', 'grid', 'random']
                        current_idx = distributions.index(self.distribution)
                        self.distribution = distributions[(current_idx + 1) % 3]
                        print(f"Distribution: {self.distribution}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.major_radius = min(5.0, self.major_radius + 0.1)
                        print(f"Major radius: {self.major_radius:.1f}")
                    elif event.key == pygame.K_MINUS:
                        self.major_radius = max(0.5, self.major_radius - 0.1)
                        print(f"Major radius: {self.major_radius:.1f}")
                    elif event.key == pygame.K_RIGHTBRACKET:
                        self.minor_radius = min(3.0, self.minor_radius + 0.1)
                        print(f"Minor radius: {self.minor_radius:.1f}")
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.minor_radius = max(0.1, self.minor_radius - 0.1)
                        print(f"Minor radius: {self.minor_radius:.1f}")
                    elif event.key == pygame.K_1:
                        self.xw_rotation_speed *= 1.2
                        print(f"XW rotation speed: {self.xw_rotation_speed:.2f}")
                    elif event.key == pygame.K_2:
                        self.yz_rotation_speed *= 1.2
                        print(f"YZ rotation speed: {self.yz_rotation_speed:.2f}")
                    elif event.key == pygame.K_3:
                        self.zw_rotation_speed *= 1.2
                        print(f"ZW rotation speed: {self.zw_rotation_speed:.2f}")
                    elif event.key == pygame.K_x:
                        self.stereoscopic_mode = (self.stereoscopic_mode + 1) % 3
                        modes = ['Off', 'Side-by-side', 'Anaglyph (red/cyan)']
                        print(f"Stereoscopic mode: {modes[self.stereoscopic_mode]}")
                        if self.stereoscopic_mode == 2:
                            print("  (You'll need red/cyan 3D glasses for anaglyph mode)")
                    elif event.key == pygame.K_COMMA:
                        self.eye_separation = max(0.05, self.eye_separation - 0.05)
                        print(f"Eye separation: {self.eye_separation:.2f}")
                    elif event.key == pygame.K_PERIOD:
                        self.eye_separation = min(1.0, self.eye_separation + 0.05)
                        print(f"Eye separation: {self.eye_separation:.2f}")
                    elif event.key == pygame.K_LESS:
                        self.convergence_distance = max(1.0, self.convergence_distance - 0.5)
                        print(f"Convergence distance: {self.convergence_distance:.1f}")
                    elif event.key == pygame.K_GREATER:
                        self.convergence_distance = min(20.0, self.convergence_distance + 0.5)
                        print(f"Convergence distance: {self.convergence_distance:.1f}")
            
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
        viewer = GPU4DToroidViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Check your graphics drivers are up to date")
        print("3. Try reducing point_count if performance is poor")

if __name__ == "__main__":
    main()