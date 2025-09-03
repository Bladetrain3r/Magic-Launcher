import math
import sys
import os
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
import ctypes
import time

class GPUElectronCloudViewer:
    def __init__(self):
        # Quantum numbers
        self.n = 1  # Principal quantum number (1-4)
        self.l = 0  # Azimuthal quantum number (0 to n-1)
        self.m = 0  # Magnetic quantum number (-l to +l)
        
        # Visualization parameters
        self.point_count = 100000
        self.cloud_scale = 5.0
        self.probability_threshold = 0.001
        self.show_probability_density = True
        self.show_phase = False
        self.show_radial_nodes = False
        self.show_angular_nodes = False
        
        # Display modes
        self.visualization_mode = 0  # 0: Probability cloud, 1: Isosurface, 2: Cross-section
        self.color_mode = 0  # 0: Probability density, 1: Phase, 2: Energy levels
        
        # Animation
        self.animate_phase = False
        self.phase_speed = 0.5
        self.rotate_orbital = False
        self.rotation_speed = 0.5
        
        # Camera settings
        self.camera_pos = [0, 0, 10]
        self.rotation = [0, 0, 0]
        self.auto_rotate = False
        self.auto_rotate_speed = [0.2, 0.3]
        
        # Display settings
        self.width = 1280
        self.height = 1280
        self.base_point_size = 1.5
        self.brightness = 1.0
        
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
        pygame.display.set_caption("GPU Electron Cloud Visualization")
        
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
        """Create vertex and fragment shaders for electron cloud rendering"""
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in float index;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time;
        uniform int n;  // Principal quantum number
        uniform int l;  // Azimuthal quantum number
        uniform int m;  // Magnetic quantum number
        uniform float cloud_scale;
        uniform float point_count;
        uniform int visualization_mode;
        uniform float phase_speed;
        uniform bool animate_phase;
        uniform float rotation_angle;
        uniform float base_point_size;
        
        out vec3 FragPos;
        out float ProbabilityDensity;
        out float WavePhase;
        out float RadialPart;
        out float AngularPart;
        out vec3 OrbitalColor;
        
        const float PI = 3.14159265359;
        const float BOHR_RADIUS = 1.0;  // Normalized
        
        // Factorial function (limited but sufficient for our needs)
        float factorial(int n) {
            float result = 1.0;
            for (int i = 2; i <= n; i++) {
                result *= float(i);
            }
            return result;
        }
        
        // Associated Laguerre polynomial
        float laguerre(float x, int n, int l) {
            if (n == 1) return 1.0;
            if (n == 2) {
                if (l == 0) return 2.0 - x;
                if (l == 1) return -x + 4.0;
            }
            if (n == 3) {
                if (l == 0) return 6.0 - 6.0*x + x*x;
                if (l == 1) return -4.0*x + x*x + 12.0;
                if (l == 2) return x*x - 8.0*x + 12.0;
            }
            return 1.0;  // Fallback
        }
        
        // Legendre polynomial
        float legendre(float x, int l, int m) {
            float result = 1.0;
            
            if (l == 0) result = 1.0;
            else if (l == 1) {
                if (abs(m) == 0) result = x;
                else if (abs(m) == 1) result = -sqrt(1.0 - x*x);
            }
            else if (l == 2) {
                if (abs(m) == 0) result = 0.5 * (3.0*x*x - 1.0);
                else if (abs(m) == 1) result = -3.0 * x * sqrt(1.0 - x*x);
                else if (abs(m) == 2) result = 3.0 * (1.0 - x*x);
            }
            else if (l == 3) {
                if (abs(m) == 0) result = 0.5 * x * (5.0*x*x - 3.0);
                else if (abs(m) == 1) result = -1.5 * (5.0*x*x - 1.0) * sqrt(1.0 - x*x);
                else if (abs(m) == 2) result = 15.0 * x * (1.0 - x*x);
                else if (abs(m) == 3) result = -15.0 * pow(1.0 - x*x, 1.5);
            }
            
            return result;
        }
        
        // Radial wave function
        float radial_wavefunction(float r, int n, int l) {
            float rho = 2.0 * r / (float(n) * BOHR_RADIUS);
            
            // Normalization constant
            float norm = sqrt(pow(2.0/(float(n)*BOHR_RADIUS), 3.0) * 
                           factorial(n-l-1) / (2.0*float(n)*factorial(n+l)));
            
            // Radial part
            float radial = norm * exp(-rho/2.0) * pow(rho, float(l)) * 
                          laguerre(rho, n-l-1, 2*l+1);
            
            return radial;
        }
        
        // Angular wave function (spherical harmonics)
        vec2 spherical_harmonic(float theta, float phi, int l, int m) {
            // Normalization
            float norm = sqrt((2.0*float(l)+1.0)/(4.0*PI) * 
                            factorial(l-abs(m))/factorial(l+abs(m)));
            
            // Angular part
            float angular = norm * legendre(cos(theta), l, abs(m));
            
            // Phase part (complex number as vec2)
            float real_part = angular * cos(float(m) * phi);
            float imag_part = angular * sin(float(m) * phi);
            
            return vec2(real_part, imag_part);
        }
        
        vec3 sample_electron_position(float idx) {
            // Use stratified sampling for better distribution
            float u1 = fract(sin(idx * 12.9898) * 43758.5453);
            float u2 = fract(sin(idx * 78.233) * 43758.5453);
            float u3 = fract(sin(idx * 45.164) * 43758.5453);
            
            vec3 pos;
            
            if (visualization_mode == 0) {
                // Monte Carlo sampling of probability distribution
                // Sample in spherical coordinates with importance sampling
                
                // Radial sampling weighted by r² (volume element)
                float r = cloud_scale * pow(u1, 1.0/3.0) * float(n) * 2.0;
                
                // Angular sampling
                float theta = acos(2.0 * u2 - 1.0);  // Uniform on sphere
                float phi = 2.0 * PI * u3;
                
                // Convert to Cartesian
                pos.x = r * sin(theta) * cos(phi);
                pos.y = r * sin(theta) * sin(phi);
                pos.z = r * cos(theta);
                
                // Calculate wave function
                float radial = radial_wavefunction(r, n, l);
                vec2 angular = spherical_harmonic(theta, phi, l, m);
                
                // Probability density |ψ|²
                float psi_squared = radial * radial * (angular.x * angular.x + angular.y * angular.y);
                ProbabilityDensity = psi_squared;
                
                // Rejection sampling
                float acceptance = fract(sin(idx * 94.673) * 43758.5453);
                if (psi_squared < acceptance * 0.1) {
                    // Reject this point - place it far away
                    pos *= 100.0;
                    ProbabilityDensity = 0.0;
                }
                
                // Store components for visualization
                RadialPart = abs(radial);
                AngularPart = length(angular);
                WavePhase = atan(angular.y, angular.x);
                
            } else if (visualization_mode == 1) {
                // Isosurface visualization
                float theta = u1 * PI;
                float phi = u2 * 2.0 * PI;
                
                // Find radius for constant probability
                float target_prob = 0.05;  // Isosurface level
                float r = float(n) * BOHR_RADIUS * (1.0 + u3 * 3.0);
                
                // Spherical to Cartesian
                pos.x = r * sin(theta) * cos(phi) * cloud_scale;
                pos.y = r * sin(theta) * sin(phi) * cloud_scale;
                pos.z = r * cos(theta) * cloud_scale;
                
                // Calculate wave function
                float radial = radial_wavefunction(r, n, l);
                vec2 angular = spherical_harmonic(theta, phi, l, m);
                
                ProbabilityDensity = radial * radial * (angular.x * angular.x + angular.y * angular.y);
                RadialPart = abs(radial);
                AngularPart = length(angular);
                WavePhase = atan(angular.y, angular.x);
                
            } else {
                // Cross-section visualization
                float angle = u1 * 2.0 * PI;
                float radius = u2 * cloud_scale * float(n) * 2.0;
                
                // Place points in a plane
                pos.x = radius * cos(angle);
                pos.y = radius * sin(angle);
                pos.z = (u3 - 0.5) * 0.1;  // Thin slice
                
                float r = length(pos);
                float theta = acos(pos.z / max(r, 0.001));
                float phi = atan(pos.y, pos.x);
                
                // Calculate wave function
                float radial = radial_wavefunction(r, n, l);
                vec2 angular = spherical_harmonic(theta, phi, l, m);
                
                ProbabilityDensity = radial * radial * (angular.x * angular.x + angular.y * angular.y);
                RadialPart = abs(radial);
                AngularPart = length(angular);
                WavePhase = atan(angular.y, angular.x);
            }
            
            // Apply rotation if enabled
            if (rotation_angle != 0.0) {
                float c = cos(rotation_angle);
                float s = sin(rotation_angle);
                float y = pos.y;
                pos.y = y * c - pos.z * s;
                pos.z = y * s + pos.z * c;
            }
            
            return pos;
        }
        
        void main()
        {
            // Generate electron position
            vec3 pos = sample_electron_position(index);
            FragPos = pos;
            
            // Orbital-specific coloring
            if (l == 0) {  // s orbital - spherical
                OrbitalColor = vec3(1.0, 0.5, 0.5);  // Reddish
            } else if (l == 1) {  // p orbital - dumbbell
                OrbitalColor = vec3(0.5, 1.0, 0.5);  // Greenish
            } else if (l == 2) {  // d orbital - cloverleaf
                OrbitalColor = vec3(0.5, 0.5, 1.0);  // Bluish
            } else {  // f orbital - complex
                OrbitalColor = vec3(1.0, 1.0, 0.5);  // Yellowish
            }
            
            // Apply phase animation
            if (animate_phase) {
                WavePhase += time * phase_speed;
            }
            
            // Apply transformations
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Point size based on probability density
            gl_PointSize = base_point_size * (1.0 + 2.0 * ProbabilityDensity);
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in float ProbabilityDensity;
        in float WavePhase;
        in float RadialPart;
        in float AngularPart;
        in vec3 OrbitalColor;
        
        uniform int color_mode;
        uniform float brightness;
        uniform bool show_phase;
        uniform bool show_radial_nodes;
        uniform bool show_angular_nodes;
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
            // Skip points with very low probability
            if (ProbabilityDensity < 0.0001) {
                discard;
            }
            
            vec3 color;
            
            if (color_mode == 0) {
                // Probability density coloring
                float intensity = pow(ProbabilityDensity * 10.0, 0.5);
                color = OrbitalColor * intensity;
                
                // Add glow effect for high probability regions
                if (ProbabilityDensity > 0.05) {
                    color += vec3(0.2, 0.2, 0.3) * (ProbabilityDensity - 0.05) * 5.0;
                }
                
            } else if (color_mode == 1) {
                // Phase coloring
                float phase = WavePhase + (show_phase ? time * 0.5 : 0.0);
                float hue = mod(phase * 57.2958 + 180.0, 360.0);
                float saturation = 0.8;
                float value = 0.3 + 0.7 * ProbabilityDensity * 10.0;
                color = hsv_to_rgb(vec3(hue, saturation, value));
                
            } else {
                // Energy level coloring
                float energy_color = 1.0 - exp(-ProbabilityDensity * 5.0);
                
                // Cool to warm gradient based on energy
                vec3 cool = vec3(0.0, 0.0, 1.0);
                vec3 warm = vec3(1.0, 0.0, 0.0);
                color = mix(cool, warm, energy_color);
            }
            
            // Show nodes if enabled
            if (show_radial_nodes && RadialPart < 0.01) {
                color = vec3(1.0, 1.0, 0.0);  // Yellow for radial nodes
            }
            if (show_angular_nodes && AngularPart < 0.01) {
                color = vec3(0.0, 1.0, 1.0);  // Cyan for angular nodes
            }
            
            // Apply brightness
            color *= brightness;
            
            // Distance fade
            float dist = length(FragPos);
            float fade = 1.0 - smoothstep(10.0, 20.0, dist);
            
            // Add slight transparency for depth
            float alpha = 0.8 * fade * (0.3 + 0.7 * ProbabilityDensity);
            
            FragColor = vec4(color, alpha);
        }
        """
        
        try:
            # Compile shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            print("Electron cloud shaders compiled successfully!")
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
        
        # Enable blending for transparency
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
        far = 100.0
        
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
        current_time = pygame.time.get_ticks() * 0.001
        
        # Calculate rotation angle if orbital rotation is enabled
        rotation_angle = current_time * self.rotation_speed if self.rotate_orbital else 0.0
        
        # Set uniforms
        uniforms = {
            'projection': glGetUniformLocation(self.shader_program, "projection"),
            'view': glGetUniformLocation(self.shader_program, "view"),
            'model': glGetUniformLocation(self.shader_program, "model"),
            'time': glGetUniformLocation(self.shader_program, "time"),
            'n': glGetUniformLocation(self.shader_program, "n"),
            'l': glGetUniformLocation(self.shader_program, "l"),
            'm': glGetUniformLocation(self.shader_program, "m"),
            'cloud_scale': glGetUniformLocation(self.shader_program, "cloud_scale"),
            'point_count': glGetUniformLocation(self.shader_program, "point_count"),
            'visualization_mode': glGetUniformLocation(self.shader_program, "visualization_mode"),
            'phase_speed': glGetUniformLocation(self.shader_program, "phase_speed"),
            'animate_phase': glGetUniformLocation(self.shader_program, "animate_phase"),
            'rotation_angle': glGetUniformLocation(self.shader_program, "rotation_angle"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode"),
            'brightness': glGetUniformLocation(self.shader_program, "brightness"),
            'show_phase': glGetUniformLocation(self.shader_program, "show_phase"),
            'show_radial_nodes': glGetUniformLocation(self.shader_program, "show_radial_nodes"),
            'show_angular_nodes': glGetUniformLocation(self.shader_program, "show_angular_nodes"),
            'base_point_size': glGetUniformLocation(self.shader_program, "base_point_size")
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
        glUniform1i(uniforms['n'], self.n)
        glUniform1i(uniforms['l'], self.l)
        glUniform1i(uniforms['m'], self.m)
        glUniform1f(uniforms['cloud_scale'], self.cloud_scale)
        glUniform1f(uniforms['point_count'], self.point_count)
        glUniform1i(uniforms['visualization_mode'], self.visualization_mode)
        glUniform1f(uniforms['phase_speed'], self.phase_speed)
        glUniform1i(uniforms['animate_phase'], self.animate_phase)
        glUniform1f(uniforms['rotation_angle'], rotation_angle)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        glUniform1f(uniforms['brightness'], self.brightness)
        glUniform1i(uniforms['show_phase'], self.show_phase)
        glUniform1i(uniforms['show_radial_nodes'], self.show_radial_nodes)
        glUniform1i(uniforms['show_angular_nodes'], self.show_angular_nodes)
        glUniform1f(uniforms['base_point_size'], self.base_point_size)
        
        # Draw
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)
        
        pygame.display.flip()

    def get_orbital_name(self):
        """Get the name of the current orbital"""
        orbital_letters = ['s', 'p', 'd', 'f']
        if self.l < len(orbital_letters):
            return f"{self.n}{orbital_letters[self.l]}"
        return f"{self.n}l={self.l}"

    def run(self):
        """Main loop"""
        # Initialize
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nGPU Electron Cloud Visualization")
        print(f"\nCurrent orbital: {self.get_orbital_name()}")
        print("\nControls:")
        print("  Arrow keys: Rotate view")
        print("  Page Up/Down: Zoom in/out")
        print("  1-4: Set principal quantum number (n)")
        print("  Q/E: Decrease/Increase azimuthal number (l)")
        print("  A/D: Decrease/Increase magnetic number (m)")
        print("  C: Cycle color modes")
        print("  V: Cycle visualization modes")
        print("  P: Toggle phase animation")
        print("  R: Toggle orbital rotation")
        print("  N: Show/hide radial nodes")
        print("  M: Show/hide angular nodes")
        print("  +/-: Adjust brightness")
        print("  Space: Reset view")
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
                    elif event.key == pygame.K_SPACE:
                        # Reset view
                        self.camera_pos = [0, 0, 10]
                        self.rotation = [0, 0, 0]
                        self.n = 1
                        self.l = 0
                        self.m = 0
                        print(f"Reset to {self.get_orbital_name()} orbital")
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] -= 1
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] += 1
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        self.n = int(event.unicode)
                        # Adjust l and m if necessary
                        if self.l >= self.n:
                            self.l = self.n - 1
                        if abs(self.m) > self.l:
                            self.m = 0
                        print(f"Orbital: {self.get_orbital_name()}, m={self.m}")
                    elif event.key == pygame.K_q:
                        if self.l > 0:
                            self.l -= 1
                            if abs(self.m) > self.l:
                                self.m = 0
                            print(f"Orbital: {self.get_orbital_name()}, m={self.m}")
                    elif event.key == pygame.K_e:
                        if self.l < self.n - 1:
                            self.l += 1
                            print(f"Orbital: {self.get_orbital_name()}, m={self.m}")
                    elif event.key == pygame.K_a:
                        if self.m > -self.l:
                            self.m -= 1
                            print(f"Orbital: {self.get_orbital_name()}, m={self.m}")
                    elif event.key == pygame.K_d:
                        if self.m < self.l:
                            self.m += 1
                            print(f"Orbital: {self.get_orbital_name()}, m={self.m}")
                    elif event.key == pygame.K_c:
                        self.color_mode = (self.color_mode + 1) % 3
                        modes = ['Probability density', 'Wave phase', 'Energy levels']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_v:
                        self.visualization_mode = (self.visualization_mode + 1) % 3
                        modes = ['Probability cloud', 'Isosurface', 'Cross-section']
                        print(f"Visualization: {modes[self.visualization_mode]}")
                    elif event.key == pygame.K_p:
                        self.animate_phase = not self.animate_phase
                        print(f"Phase animation: {'ON' if self.animate_phase else 'OFF'}")
                    elif event.key == pygame.K_r:
                        self.rotate_orbital = not self.rotate_orbital
                        print(f"Orbital rotation: {'ON' if self.rotate_orbital else 'OFF'}")
                    elif event.key == pygame.K_n:
                        self.show_radial_nodes = not self.show_radial_nodes
                        print(f"Radial nodes: {'ON' if self.show_radial_nodes else 'OFF'}")
                    elif event.key == pygame.K_m:
                        self.show_angular_nodes = not self.show_angular_nodes
                        print(f"Angular nodes: {'ON' if self.show_angular_nodes else 'OFF'}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.brightness = min(2.0, self.brightness + 0.1)
                        print(f"Brightness: {self.brightness:.1f}")
                    elif event.key == pygame.K_MINUS:
                        self.brightness = max(0.1, self.brightness - 0.1)
                        print(f"Brightness: {self.brightness:.1f}")
            
            # Handle continuous rotation
            keys = pygame.key.get_pressed()
            if self.auto_rotate:
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
        viewer = GPUElectronCloudViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Check your graphics drivers are up to date")

if __name__ == "__main__":
    main()