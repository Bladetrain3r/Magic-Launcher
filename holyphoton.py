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

class GPUPhotonWaveViewer:
    def __init__(self):
        # Wave parameters
        self.wavelength = 1.0  # Base wavelength
        self.frequency = 1.0   # Frequency (c/wavelength)
        self.amplitude = 0.5   # Wave amplitude
        self.propagation_speed = 1.0  # Speed of light (normalized)
        self.polarization_angle = 0.0  # Polarization angle
        self.phase_offset = 0.0
        
        # Visualization parameters
        self.wave_segments = 1000  # Points along the wave
        self.field_lines = 20      # Number of field lines to show
        self.wave_length_display = 10.0  # How many wavelengths to show
        self.show_electric = True
        self.show_magnetic = True
        self.show_envelope = True
        self.show_poynting = False  # Poynting vector (energy flow)
        self.show_quantum_probability = False
        
        # Display modes
        self.visualization_mode = 0  # 0: Classic EM, 1: Quantum wave packet, 2: Photon stream
        self.color_mode = 0  # 0: Standard, 1: Frequency-based, 2: Energy density
        
        # Camera settings
        self.camera_pos = [0, 0, 6]
        self.rotation = [-20, 0, 0]
        self.auto_rotate = False
        self.auto_rotate_speed = [0.0, 0.5]
        
        # Display settings
        self.width = 1280
        self.height = 1280
        self.base_point_size = 2.0
        self.line_width = 2.0
        
        # Animation
        self.time_scale = 1.0
        self.paused = False
        
        # OpenGL objects
        self.shader_program = None
        self.wave_vao = None
        self.wave_vbo = None
        self.field_vao = None
        self.field_vbo = None
        self.vertex_count = 0
        self.field_vertex_count = 0

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
        pygame.display.set_caption("GPU Photon Wave Visualization")
        
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
        """Create vertex and fragment shaders for photon wave rendering"""
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in float index;
        layout(location = 1) in float field_type; // 0=wave, 1=E-field, 2=B-field, 3=poynting
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time;
        uniform float wavelength;
        uniform float frequency;
        uniform float amplitude;
        uniform float propagation_speed;
        uniform float polarization_angle;
        uniform float phase_offset;
        uniform float wave_length_display;
        uniform int wave_segments;
        uniform int field_lines;
        uniform int visualization_mode;
        uniform bool show_quantum_probability;
        
        out vec3 FragPos;
        out vec3 FieldType;
        out float Intensity;
        out float Phase;
        out float QuantumProb;
        
        const float PI = 3.14159265359;
        const float TWO_PI = 6.28318530718;
        
        vec3 calculate_wave_position(float x) {
            vec3 pos = vec3(x, 0.0, 0.0);
            
            if (visualization_mode == 0) {
                // Classic electromagnetic wave
                float k = TWO_PI / wavelength;  // Wave number
                float omega = TWO_PI * frequency;  // Angular frequency
                float phase = k * x - omega * time * propagation_speed + phase_offset;
                
                // Electric field (Y direction)
                float E_y = amplitude * sin(phase);
                
                // Magnetic field (Z direction)
                float B_z = amplitude * sin(phase);
                
                if (field_type == 0.0) {
                    // Main wave visualization - show as a helix
                    pos.y = E_y * cos(polarization_angle);
                    pos.z = E_y * sin(polarization_angle);
                } else if (field_type == 1.0) {
                    // Electric field lines
                    float line_idx = mod(index, float(field_lines));
                    float angle = (line_idx / float(field_lines)) * TWO_PI;
                    pos.y = E_y * (0.5 + 0.5 * cos(angle));
                    pos.z = 0.0;
                } else if (field_type == 2.0) {
                    // Magnetic field lines
                    float line_idx = mod(index, float(field_lines));
                    float angle = (line_idx / float(field_lines)) * TWO_PI;
                    pos.y = 0.0;
                    pos.z = B_z * (0.5 + 0.5 * cos(angle));
                } else {
                    // Poynting vector visualization
                    pos.y = E_y * 0.3;
                    pos.z = B_z * 0.3;
                }
                
                Phase = phase;
                Intensity = E_y * E_y + B_z * B_z;  // Energy density
                
            } else if (visualization_mode == 1) {
                // Quantum wave packet
                float k = TWO_PI / wavelength;
                float omega = TWO_PI * frequency;
                float phase = k * x - omega * time * propagation_speed + phase_offset;
                
                // Gaussian envelope for wave packet
                float packet_width = wavelength * 5.0;
                float packet_center = mod(time * propagation_speed, wave_length_display) - wave_length_display * 0.5;
                float envelope = exp(-(x - packet_center) * (x - packet_center) / (packet_width * packet_width));
                
                // Modulated wave
                float wave = amplitude * sin(phase) * envelope;
                
                if (field_type == 0.0) {
                    // Probability amplitude visualization
                    pos.y = wave * cos(polarization_angle);
                    pos.z = wave * sin(polarization_angle);
                    QuantumProb = envelope * envelope;  // |ψ|²
                } else {
                    // Field visualization for quantum case
                    pos.y = wave;
                    pos.z = wave * 0.5;
                    QuantumProb = envelope * envelope;
                }
                
                Phase = phase;
                Intensity = wave * wave;
                
            } else {
                // Photon stream visualization
                float photon_spacing = wavelength;
                float photon_idx = floor(x / photon_spacing);
                float photon_phase = mod(photon_idx * PI + time * frequency * TWO_PI, TWO_PI);
                
                // Create discrete photon packets
                float local_x = mod(x, photon_spacing) / photon_spacing;
                float photon_envelope = smoothstep(0.0, 0.3, local_x) * smoothstep(1.0, 0.7, local_x);
                
                // Helical motion for photon
                float helix_phase = photon_phase + local_x * TWO_PI;
                pos.y = amplitude * photon_envelope * cos(helix_phase + polarization_angle);
                pos.z = amplitude * photon_envelope * sin(helix_phase + polarization_angle);
                
                Phase = helix_phase;
                Intensity = photon_envelope;
                QuantumProb = photon_envelope;
            }
            
            FieldType = vec3(field_type, 0.0, 0.0);
            return pos;
        }
        
        void main()
        {
            // Calculate position along wave
            float x = (index / float(wave_segments)) * wave_length_display - wave_length_display * 0.5;
            
            // Get wave position
            vec3 pos = calculate_wave_position(x);
            FragPos = pos;
            
            // Apply transformations
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Point size based on field type and intensity
            float size_mult = 1.0;
            if (field_type == 0.0) size_mult = 2.0;      // Wave points larger
            else if (field_type < 3.0) size_mult = 1.5;  // Field lines medium
            else size_mult = 1.0;                        // Other visualizations
            
            gl_PointSize = 2.0 * size_mult * (0.5 + 0.5 * sqrt(Intensity));
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec3 FieldType;
        in float Intensity;
        in float Phase;
        in float QuantumProb;
        
        uniform int color_mode;
        uniform float wavelength;
        uniform bool show_quantum_probability;
        
        out vec4 FragColor;
        
        vec3 wavelength_to_rgb(float wavelength_nm) {
            // Convert wavelength (380-780 nm) to RGB
            vec3 color;
            
            if (wavelength_nm < 380.0) {
                color = vec3(1.0, 0.0, 1.0);  // Ultraviolet as violet
            } else if (wavelength_nm < 440.0) {
                float t = (wavelength_nm - 380.0) / 60.0;
                color = mix(vec3(1.0, 0.0, 1.0), vec3(0.0, 0.0, 1.0), t);
            } else if (wavelength_nm < 490.0) {
                float t = (wavelength_nm - 440.0) / 50.0;
                color = mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 1.0), t);
            } else if (wavelength_nm < 510.0) {
                float t = (wavelength_nm - 490.0) / 20.0;
                color = mix(vec3(0.0, 1.0, 1.0), vec3(0.0, 1.0, 0.0), t);
            } else if (wavelength_nm < 580.0) {
                float t = (wavelength_nm - 510.0) / 70.0;
                color = mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 1.0, 0.0), t);
            } else if (wavelength_nm < 645.0) {
                float t = (wavelength_nm - 580.0) / 65.0;
                color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.5, 0.0), t);
            } else if (wavelength_nm < 780.0) {
                float t = (wavelength_nm - 645.0) / 135.0;
                color = mix(vec3(1.0, 0.5, 0.0), vec3(1.0, 0.0, 0.0), t);
            } else {
                color = vec3(1.0, 0.0, 0.0);  // Infrared as red
            }
            
            return color;
        }
        
        void main()
        {
            vec3 color;
            
            if (color_mode == 0) {
                // Standard coloring based on field type
                if (FieldType.x == 0.0) {
                    // Wave - white to cyan gradient
                    color = mix(vec3(1.0, 1.0, 1.0), vec3(0.0, 1.0, 1.0), 0.5 + 0.5 * sin(Phase));
                } else if (FieldType.x == 1.0) {
                    // Electric field - yellow
                    color = vec3(1.0, 1.0, 0.0) * (0.5 + 0.5 * Intensity);
                } else if (FieldType.x == 2.0) {
                    // Magnetic field - magenta
                    color = vec3(1.0, 0.0, 1.0) * (0.5 + 0.5 * Intensity);
                } else {
                    // Poynting vector - green
                    color = vec3(0.0, 1.0, 0.0) * Intensity;
                }
                
            } else if (color_mode == 1) {
                // Frequency-based coloring (visible spectrum)
                float wavelength_nm = wavelength * 500.0;  // Scale to nanometers
                color = wavelength_to_rgb(wavelength_nm);
                color *= (0.5 + 0.5 * Intensity);
                
            } else {
                // Energy density coloring
                float energy = Intensity;
                if (show_quantum_probability && QuantumProb > 0.0) {
                    energy = QuantumProb;
                }
                
                // Heat map: blue -> green -> yellow -> red
                if (energy < 0.25) {
                    color = mix(vec3(0.0, 0.0, 0.5), vec3(0.0, 0.0, 1.0), energy * 4.0);
                } else if (energy < 0.5) {
                    color = mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 0.0), (energy - 0.25) * 4.0);
                } else if (energy < 0.75) {
                    color = mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 1.0, 0.0), (energy - 0.5) * 4.0);
                } else {
                    color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), (energy - 0.75) * 4.0);
                }
            }
            
            // Add quantum probability overlay if enabled
            if (show_quantum_probability && QuantumProb > 0.01) {
                color = mix(color, vec3(0.5, 0.5, 1.0), QuantumProb * 0.3);
            }
            
            // Fade based on distance
            float dist = length(FragPos);
            float fade = 1.0 - smoothstep(5.0, 15.0, dist);
            
            FragColor = vec4(color * fade, 1.0);
        }
        """
        
        try:
            # Compile shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            print("Photon wave shaders compiled successfully!")
        except Exception as e:
            print(f"Shader compilation error: {e}")
            raise

    def create_vertex_buffers(self):
        """Create vertex buffers for wave and field lines"""
        # Create wave vertex buffer
        wave_indices = np.arange(self.wave_segments, dtype=np.float32)
        wave_types = np.zeros(self.wave_segments, dtype=np.float32)  # All type 0 for wave
        wave_data = np.column_stack([wave_indices, wave_types]).flatten()
        
        # Create VAO and VBO for wave
        self.wave_vao = glGenVertexArrays(1)
        glBindVertexArray(self.wave_vao)
        
        self.wave_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.wave_vbo)
        glBufferData(GL_ARRAY_BUFFER, wave_data.nbytes, wave_data, GL_DYNAMIC_DRAW)
        
        # Set vertex attributes for wave
        stride = 2 * ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        self.vertex_count = self.wave_segments
        
        # Create field lines vertex buffer
        field_points = self.wave_segments * self.field_lines
        field_indices = np.tile(np.arange(self.wave_segments), self.field_lines).astype(np.float32)
        e_field_types = np.ones(field_points, dtype=np.float32)  # Type 1 for E-field
        b_field_types = np.full(field_points, 2.0, dtype=np.float32)  # Type 2 for B-field
        
        # Combine E and B field data
        field_data = np.concatenate([
            np.column_stack([field_indices, e_field_types]).flatten(),
            np.column_stack([field_indices, b_field_types]).flatten()
        ])
        
        # Create VAO and VBO for fields
        self.field_vao = glGenVertexArrays(1)
        glBindVertexArray(self.field_vao)
        
        self.field_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.field_vbo)
        glBufferData(GL_ARRAY_BUFFER, field_data.nbytes, field_data, GL_DYNAMIC_DRAW)
        
        # Set vertex attributes for fields
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        self.field_vertex_count = field_points * 2  # E and B fields
        
        print(f"Created vertex buffers: {self.vertex_count} wave points, {self.field_vertex_count} field points")

    def init_gl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.0, 0.0, 0.05, 1.0)  # Very dark blue background
        
        # Enable point size control from shaders
        glEnable(GL_PROGRAM_POINT_SIZE)
        
        # Enable line width (though modern OpenGL limits this)
        glLineWidth(self.line_width)
        
        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Create shaders and vertex buffers
        self.create_shaders()
        self.create_vertex_buffers()
        
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
        current_time = pygame.time.get_ticks() * 0.001 * self.time_scale if not self.paused else self.phase_offset
        
        # Set uniforms
        uniforms = {
            'projection': glGetUniformLocation(self.shader_program, "projection"),
            'view': glGetUniformLocation(self.shader_program, "view"),
            'model': glGetUniformLocation(self.shader_program, "model"),
            'time': glGetUniformLocation(self.shader_program, "time"),
            'wavelength': glGetUniformLocation(self.shader_program, "wavelength"),
            'frequency': glGetUniformLocation(self.shader_program, "frequency"),
            'amplitude': glGetUniformLocation(self.shader_program, "amplitude"),
            'propagation_speed': glGetUniformLocation(self.shader_program, "propagation_speed"),
            'polarization_angle': glGetUniformLocation(self.shader_program, "polarization_angle"),
            'phase_offset': glGetUniformLocation(self.shader_program, "phase_offset"),
            'wave_length_display': glGetUniformLocation(self.shader_program, "wave_length_display"),
            'wave_segments': glGetUniformLocation(self.shader_program, "wave_segments"),
            'field_lines': glGetUniformLocation(self.shader_program, "field_lines"),
            'visualization_mode': glGetUniformLocation(self.shader_program, "visualization_mode"),
            'show_quantum_probability': glGetUniformLocation(self.shader_program, "show_quantum_probability"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode")
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
        glUniform1f(uniforms['wavelength'], self.wavelength)
        glUniform1f(uniforms['frequency'], self.frequency)
        glUniform1f(uniforms['amplitude'], self.amplitude)
        glUniform1f(uniforms['propagation_speed'], self.propagation_speed)
        glUniform1f(uniforms['polarization_angle'], self.polarization_angle)
        glUniform1f(uniforms['phase_offset'], self.phase_offset)
        glUniform1f(uniforms['wave_length_display'], self.wave_length_display)
        glUniform1i(uniforms['wave_segments'], self.wave_segments)
        glUniform1i(uniforms['field_lines'], self.field_lines)
        glUniform1i(uniforms['visualization_mode'], self.visualization_mode)
        glUniform1i(uniforms['show_quantum_probability'], self.show_quantum_probability)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        
        # Draw wave
        glBindVertexArray(self.wave_vao)
        glDrawArrays(GL_LINE_STRIP, 0, self.vertex_count)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        
        # Draw field lines if enabled
        if (self.show_electric or self.show_magnetic) and self.visualization_mode == 0:
            glBindVertexArray(self.field_vao)
            if self.show_electric:
                glDrawArrays(GL_POINTS, 0, self.field_vertex_count // 2)
            if self.show_magnetic:
                glDrawArrays(GL_POINTS, self.field_vertex_count // 2, self.field_vertex_count // 2)
        
        glBindVertexArray(0)
        
        pygame.display.flip()

    def run(self):
        """Main loop"""
        # Initialize
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nGPU Photon Wave Visualization")
        print("\nControls:")
        print("  Arrow keys: Rotate view")
        print("  Page Up/Down: Zoom in/out")
        print("  W/S: Adjust wavelength")
        print("  A/D: Adjust amplitude")
        print("  Q/E: Rotate polarization")
        print("  1/2/3: Change visualization mode")
        print("  C: Cycle color modes")
        print("  F/G: Show/hide electric/magnetic fields")
        print("  P: Toggle quantum probability display")
        print("  Space: Pause/resume animation")
        print("  +/-: Adjust animation speed")
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
                        self.camera_pos = [0, 2, 5]
                        self.rotation = [-20, 0, 0]
                        self.wavelength = 1.0
                        self.amplitude = 0.5
                        self.polarization_angle = 0.0
                        print("View reset")
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] -= 0.5
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] += 0.5
                    elif event.key == pygame.K_w:
                        self.wavelength = min(3.0, self.wavelength * 1.1)
                        self.frequency = 1.0 / self.wavelength
                        print(f"Wavelength: {self.wavelength:.2f}")
                    elif event.key == pygame.K_s:
                        self.wavelength = max(0.1, self.wavelength * 0.9)
                        self.frequency = 1.0 / self.wavelength
                        print(f"Wavelength: {self.wavelength:.2f}")
                    elif event.key == pygame.K_a:
                        self.amplitude = max(0.1, self.amplitude - 0.1)
                        print(f"Amplitude: {self.amplitude:.2f}")
                    elif event.key == pygame.K_d:
                        self.amplitude = min(1.0, self.amplitude + 0.1)
                        print(f"Amplitude: {self.amplitude:.2f}")
                    elif event.key == pygame.K_q:
                        self.polarization_angle -= 0.1
                        print(f"Polarization angle: {math.degrees(self.polarization_angle):.1f}°")
                    elif event.key == pygame.K_e:
                        self.polarization_angle += 0.1
                        print(f"Polarization angle: {math.degrees(self.polarization_angle):.1f}°")
                    elif event.key == pygame.K_1:
                        self.visualization_mode = 0
                        print("Mode: Classic electromagnetic wave")
                    elif event.key == pygame.K_2:
                        self.visualization_mode = 1
                        print("Mode: Quantum wave packet")
                    elif event.key == pygame.K_3:
                        self.visualization_mode = 2
                        print("Mode: Photon stream")
                    elif event.key == pygame.K_c:
                        self.color_mode = (self.color_mode + 1) % 3
                        modes = ['Standard', 'Frequency spectrum', 'Energy density']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_f:
                        self.show_electric = not self.show_electric
                        print(f"Electric field: {'ON' if self.show_electric else 'OFF'}")
                    elif event.key == pygame.K_g:
                        self.show_magnetic = not self.show_magnetic
                        print(f"Magnetic field: {'ON' if self.show_magnetic else 'OFF'}")
                    elif event.key == pygame.K_p:
                        self.show_quantum_probability = not self.show_quantum_probability
                        print(f"Quantum probability: {'ON' if self.show_quantum_probability else 'OFF'}")
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        if self.paused:
                            self.phase_offset = pygame.time.get_ticks() * 0.001 * self.time_scale
                        print(f"Animation: {'PAUSED' if self.paused else 'RUNNING'}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.time_scale = min(5.0, self.time_scale * 1.2)
                        print(f"Time scale: {self.time_scale:.2f}x")
                    elif event.key == pygame.K_MINUS:
                        self.time_scale = max(0.1, self.time_scale * 0.8)
                        print(f"Time scale: {self.time_scale:.2f}x")
            
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
        if self.wave_vao:
            glDeleteVertexArrays(1, [self.wave_vao])
        if self.wave_vbo:
            glDeleteBuffers(1, [self.wave_vbo])
        if self.field_vao:
            glDeleteVertexArrays(1, [self.field_vao])
        if self.field_vbo:
            glDeleteBuffers(1, [self.field_vbo])
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        
        pygame.quit()

def main():
    try:
        viewer = GPUPhotonWaveViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Check your graphics drivers are up to date")

if __name__ == "__main__":
    main()