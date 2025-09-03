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

class GPUElectrostaticHypersphereViewer:
    def __init__(self):
        # Hypersphere parameters
        self.point_count = 50000  # Fewer points for electrostatic simulation
        self.initial_distribution = 'fibonacci'  # Starting distribution
        
        # Electrostatic parameters
        self.charge_strength = 0.1  # Base charge strength
        self.w_charge_multiplier = 2.0  # How much W affects charge
        self.repulsion_power = 2.0  # Inverse square law by default
        self.damping = 0.95  # Velocity damping for stability
        self.time_step = 0.01  # Simulation time step
        self.simulate = True  # Toggle simulation
        self.show_field_lines = False
        self.show_charge_gradient = True
        
        # 4D parameters
        self.w_angle = 0.0
        self.w_position = 0.0
        self.xw_rotation_speed = 0.3
        self.yz_rotation_speed = 0.2
        self.zw_rotation_speed = 0.15
        self.xy_rotation_speed = 0.25
        self.auto_rotate_4d = False
        
        # 3D camera settings
        self.camera_pos = [0, 0, 5]
        self.rotation = [0, 0, 0]
        self.auto_rotate_3d = False
        self.auto_rotate_speed = [0.5, 0.5]
        
        # Display settings
        self.width = 2560
        self.height = 1440
        self.fullscreen = True  # Fullscreen mode
        self.base_point_size = 1.0
        self.color_mode = 0  # 0: charge-based, 1: velocity-based, 2: potential energy
        
        # Stereoscopic settings
        self.stereoscopic_mode = 0  # 0: off, 1: side-by-side, 2: anaglyph (red/cyan)
        self.eye_separation = 0.2  # Distance between eyes
        self.convergence_distance = 5.0  # Where eyes converge
        
        # OpenGL objects
        self.shader_program = None
        self.compute_shader = None
        self.vao = None
        self.position_buffer = None
        self.velocity_buffer = None
        self.vertex_count = 0

    def initialize_pygame_and_opengl(self):
        """Initialize Pygame and create OpenGL context"""
        pygame.init()
        
        # Set OpenGL attributes
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        
        # Create window
        display = (self.width, self.height)
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("GPU Electrostatic Hypersphere")
        
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
        """Create compute and rendering shaders"""
        # Compute shader for electrostatic simulation
        compute_shader_source = """
        #version 430 core
        
        layout(local_size_x = 64) in;
        
        layout(std430, binding = 0) buffer PositionBuffer {
            vec4 positions[];
        };
        
        layout(std430, binding = 1) buffer VelocityBuffer {
            vec4 velocities[];
        };
        
        uniform uint point_count;
        uniform float charge_strength;
        uniform float w_charge_multiplier;
        uniform float repulsion_power;
        uniform float damping;
        uniform float time_step;
        uniform float w_position;
        
        void main() {
            uint idx = gl_GlobalInvocationID.x;
            if (idx >= point_count) return;
            
            vec4 pos = positions[idx];
            vec4 vel = velocities[idx];
            vec4 force = vec4(0.0);
            
            // Calculate charge based on W coordinate
            float charge_i = charge_strength * (1.0 + abs(pos.w + w_position) * w_charge_multiplier);
            
            // Calculate electrostatic forces from all other points
            for (uint j = 0; j < point_count; j++) {
                if (j == idx) continue;
                
                vec4 other_pos = positions[j];
                vec4 diff = pos - other_pos;
                float dist_sq = dot(diff, diff);
                
                // Avoid singularity
                if (dist_sq < 0.001) dist_sq = 0.001;
                
                // Calculate other point's charge
                float charge_j = charge_strength * (1.0 + abs(other_pos.w + w_position) * w_charge_multiplier);
                
                // Electrostatic force: F = k * q1 * q2 / r^power
                float dist = sqrt(dist_sq);
                float force_magnitude = charge_i * charge_j / pow(dist, repulsion_power);
                
                // Add force contribution
                force += normalize(diff) * force_magnitude;
            }
            
            // Constraint force to keep points on unit hypersphere
            float radius = length(pos);
            vec4 radial_force = -pos * (radius - 1.0) * 50.0;  // Spring force to unit sphere
            force += radial_force;
            
            // Update velocity with damping
            vel = vel * damping + force * time_step;
            
            // Update position
            pos += vel * time_step;
            
            // Renormalize to unit hypersphere
            pos = normalize(pos);
            
            // Store updated values
            positions[idx] = pos;
            velocities[idx] = vel;
        }
        """
        
        # Vertex shader for rendering
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in vec4 position;
        layout(location = 1) in vec4 velocity;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time;
        uniform float w_angle;
        uniform float w_position;
        uniform float xw_speed;
        uniform float yz_speed;
        uniform float zw_speed;
        uniform float xy_speed;
        uniform float charge_strength;
        uniform float w_charge_multiplier;
        uniform float base_point_size;
        
        out vec3 FragPos;
        out vec4 SphereCoord4D;
        out float WCoord;
        out float ChargeStrength;
        out float Speed;
        out vec3 VelocityDir;
        
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
            
            // XY rotation
            float cos_xy = cos(total_angle * xy_speed * 0.7);
            float sin_xy = sin(total_angle * xy_speed * 0.7);
            new_x = point4d.x * cos_xy - point4d.y * sin_xy;
            new_y = point4d.x * sin_xy + point4d.y * cos_xy;
            point4d.x = new_x;
            point4d.y = new_y;
            
            // Store W coordinate for coloring
            WCoord = point4d.w;
            
            // Stereographic projection from 4D to 3D
            float projection_factor = 2.0 / (2.0 - point4d.w * 0.3);
            
            vec3 point3d;
            point3d.x = point4d.x * projection_factor;
            point3d.y = point4d.y * projection_factor;
            point3d.z = point4d.z * projection_factor;
            
            return point3d;
        }
        
        void main()
        {
            // Store 4D position
            SphereCoord4D = position;
            
            // Calculate charge strength for this point
            ChargeStrength = charge_strength * (1.0 + abs(position.w + w_position) * w_charge_multiplier);
            
            // Calculate speed
            Speed = length(velocity);
            VelocityDir = normalize(velocity.xyz);
            
            // Project to 3D
            vec3 pos = project_4d_to_3d(position);
            FragPos = pos;
            
            // Apply transformations
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Point size based on charge
            gl_PointSize = base_point_size * (1.0 + ChargeStrength * 2.0);
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec4 SphereCoord4D;
        in float WCoord;
        in float ChargeStrength;
        in float Speed;
        in vec3 VelocityDir;
        
        uniform int color_mode;
        uniform bool show_charge_gradient;
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
            
            if (color_mode == 0) {  // Charge-based coloring
                // Red = positive (high W), Blue = negative (low W)
                float charge_normalized = (WCoord + 1.0) * 0.5;
                
                if (show_charge_gradient) {
                    // Smooth gradient based on charge
                    color = mix(vec3(0.0, 0.0, 1.0), vec3(1.0, 0.0, 0.0), charge_normalized);
                    
                    // Add intensity based on charge strength
                    float intensity = 0.3 + 0.7 * ChargeStrength / 0.5;
                    color *= intensity;
                } else {
                    // Binary charge coloring
                    if (WCoord > 0.0) {
                        color = vec3(1.0, 0.2, 0.2);  // Positive charge
                    } else {
                        color = vec3(0.2, 0.2, 1.0);  // Negative charge
                    }
                }
                
                // Add glow for high charges
                if (ChargeStrength > 0.3) {
                    color += vec3(0.2, 0.2, 0.2) * (ChargeStrength - 0.3);
                }
                
            } else if (color_mode == 1) {  // Velocity-based coloring
                // Color based on speed
                float hue = Speed * 1000.0;
                float saturation = 0.8;
                float value = 0.5 + 0.5 * min(Speed * 10.0, 1.0);
                color = hsv_to_rgb(vec3(mod(hue, 360.0), saturation, value));
                
            } else {  // Potential energy visualization
                // Show regions of high/low potential
                float potential = ChargeStrength * ChargeStrength;
                
                // Heat map coloring
                if (potential < 0.25) {
                    color = mix(vec3(0.0, 0.0, 0.5), vec3(0.0, 0.0, 1.0), potential * 4.0);
                } else if (potential < 0.5) {
                    color = mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 0.0), (potential - 0.25) * 4.0);
                } else if (potential < 0.75) {
                    color = mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 1.0, 0.0), (potential - 0.5) * 4.0);
                } else {
                    color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), (potential - 0.75) * 4.0);
                }
            }
            
            // Add pulsing effect based on charge
            color *= (0.9 + 0.1 * sin(time * 0.001 + ChargeStrength * 10.0));
            
            // Distance fade
            float dist = length(FragPos);
            float fade = 1.0 - smoothstep(5.0, 15.0, dist);
            
            FragColor = vec4(color * fade, 1.0);
        }
        """
        
        try:
            # Compile compute shader
            self.compute_shader = glCreateShader(GL_COMPUTE_SHADER)
            glShaderSource(self.compute_shader, compute_shader_source)
            glCompileShader(self.compute_shader)
            
            # Check compute shader compilation
            if not glGetShaderiv(self.compute_shader, GL_COMPILE_STATUS):
                error = glGetShaderInfoLog(self.compute_shader).decode()
                raise RuntimeError(f"Compute shader compilation error: {error}")
            
            self.compute_program = glCreateProgram()
            glAttachShader(self.compute_program, self.compute_shader)
            glLinkProgram(self.compute_program)
            
            # Check program linking
            if not glGetProgramiv(self.compute_program, GL_LINK_STATUS):
                error = glGetProgramInfoLog(self.compute_program).decode()
                raise RuntimeError(f"Compute program linking error: {error}")
            
            # Compile rendering shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            
            print("Electrostatic hypersphere shaders compiled successfully!")
            
        except Exception as e:
            print(f"Shader compilation error: {e}")
            raise

    def create_buffers(self):
        """Create GPU buffers for positions and velocities"""
        # Initialize positions on unit hypersphere
        positions = np.zeros((self.point_count, 4), dtype=np.float32)
        
        if self.initial_distribution == 'fibonacci':
            # Fibonacci distribution on 4D hypersphere
            golden_ratio = (1 + np.sqrt(5)) / 2
            
            for i in range(self.point_count):
                # Generate evenly distributed points
                t = i / self.point_count
                phi1 = 2 * np.pi * i / golden_ratio
                phi2 = np.pi * t
                phi3 = 2 * np.pi * i * golden_ratio
                
                # Convert to 4D coordinates
                positions[i] = [
                    np.sin(phi2) * np.cos(phi1) * np.sin(phi3),
                    np.sin(phi2) * np.sin(phi1) * np.sin(phi3),
                    np.sin(phi2) * np.cos(phi3),
                    np.cos(phi2)
                ]
        else:
            # Random distribution
            for i in range(self.point_count):
                # Generate random 4D vector and normalize
                vec = np.random.randn(4)
                positions[i] = vec / np.linalg.norm(vec)
        
        # Initialize velocities to zero
        velocities = np.zeros((self.point_count, 4), dtype=np.float32)
        
        # Create position buffer (SSBO)
        self.position_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.position_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, positions.nbytes, positions, GL_DYNAMIC_COPY)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.position_buffer)
        
        # Create velocity buffer (SSBO)
        self.velocity_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.velocity_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, velocities.nbytes, velocities, GL_DYNAMIC_COPY)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.velocity_buffer)
        
        # Create VAO for rendering
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Bind position buffer as vertex attribute
        glBindBuffer(GL_ARRAY_BUFFER, self.position_buffer)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Bind velocity buffer as vertex attribute
        glBindBuffer(GL_ARRAY_BUFFER, self.velocity_buffer)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)
        
        self.vertex_count = self.point_count
        print(f"Created buffers for {self.vertex_count} points")

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
        
        # Create shaders and buffers
        self.create_shaders()
        self.create_buffers()
        
        print("GPU initialization complete")

    def run_compute_shader(self):
        """Execute the compute shader for electrostatic simulation"""
        if not self.simulate:
            return
            
        glUseProgram(self.compute_program)
        
        # Set uniforms
        glUniform1ui(glGetUniformLocation(self.compute_program, "point_count"), self.point_count)
        glUniform1f(glGetUniformLocation(self.compute_program, "charge_strength"), self.charge_strength)
        glUniform1f(glGetUniformLocation(self.compute_program, "w_charge_multiplier"), self.w_charge_multiplier)
        glUniform1f(glGetUniformLocation(self.compute_program, "repulsion_power"), self.repulsion_power)
        glUniform1f(glGetUniformLocation(self.compute_program, "damping"), self.damping)
        glUniform1f(glGetUniformLocation(self.compute_program, "time_step"), self.time_step)
        glUniform1f(glGetUniformLocation(self.compute_program, "w_position"), self.w_position)
        
        # Dispatch compute shader
        work_groups = (self.point_count + 63) // 64  # 64 is local_size_x
        glDispatchCompute(work_groups, 1, 1)
        
        # Memory barrier to ensure compute shader finishes
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT | GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)

    def get_projection_matrix_stereo(self, width, height, eye_offset):
        """Get perspective projection matrix with stereo offset"""
        fov = 45.0
        aspect = width / height
        near = 0.1
        far = 50.0
        
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
        # Run physics simulation
        self.run_compute_shader()
        
        # Clear screen
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
    
    def render_eye(self, x, y, width, height, eye_offset):
        """Render from a single eye perspective"""
        # Use rendering shader
        glUseProgram(self.shader_program)
        
        # Get current time
        current_time = pygame.time.get_ticks() if self.auto_rotate_4d else 0
        
        # Set uniforms
        uniforms = {
            'projection': glGetUniformLocation(self.shader_program, "projection"),
            'view': glGetUniformLocation(self.shader_program, "view"),
            'model': glGetUniformLocation(self.shader_program, "model"),
            'time': glGetUniformLocation(self.shader_program, "time"),
            'w_angle': glGetUniformLocation(self.shader_program, "w_angle"),
            'w_position': glGetUniformLocation(self.shader_program, "w_position"),
            'xw_speed': glGetUniformLocation(self.shader_program, "xw_speed"),
            'yz_speed': glGetUniformLocation(self.shader_program, "yz_speed"),
            'zw_speed': glGetUniformLocation(self.shader_program, "zw_speed"),
            'xy_speed': glGetUniformLocation(self.shader_program, "xy_speed"),
            'charge_strength': glGetUniformLocation(self.shader_program, "charge_strength"),
            'w_charge_multiplier': glGetUniformLocation(self.shader_program, "w_charge_multiplier"),
            'base_point_size': glGetUniformLocation(self.shader_program, "base_point_size"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode"),
            'show_charge_gradient': glGetUniformLocation(self.shader_program, "show_charge_gradient")
        }
        
        # Set matrices with eye offset
        projection = self.get_projection_matrix_stereo(width, height, eye_offset)
        view = self.get_view_matrix_stereo(eye_offset)
        model = np.eye(4, dtype=np.float32)
        
        glUniformMatrix4fv(uniforms['projection'], 1, GL_TRUE, projection)
        glUniformMatrix4fv(uniforms['view'], 1, GL_TRUE, view)
        glUniformMatrix4fv(uniforms['model'], 1, GL_TRUE, model)
        
        # Set other uniforms
        glUniform1f(uniforms['time'], current_time)
        glUniform1f(uniforms['w_angle'], self.w_angle)
        glUniform1f(uniforms['w_position'], self.w_position)
        glUniform1f(uniforms['xw_speed'], self.xw_rotation_speed)
        glUniform1f(uniforms['yz_speed'], self.yz_rotation_speed)
        glUniform1f(uniforms['zw_speed'], self.zw_rotation_speed)
        glUniform1f(uniforms['xy_speed'], self.xy_rotation_speed)
        glUniform1f(uniforms['charge_strength'], self.charge_strength)
        glUniform1f(uniforms['w_charge_multiplier'], self.w_charge_multiplier)
        glUniform1f(uniforms['base_point_size'], self.base_point_size)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        glUniform1i(uniforms['show_charge_gradient'], self.show_charge_gradient)
        
        # Draw points
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)

    def run(self):
        """Main loop"""
        # Initialize
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nGPU Electrostatic Hypersphere")
        print("\nControls:")
        print("  Arrow keys: Rotate 3D view")
        print("  Page Up/Down: Zoom in/out")
        print("  W/S: Rotate in 4D (W dimension)")
        print("  T/G: Pan along W axis (affects charge distribution)")
        print("  Q/E: Decrease/Increase charge strength")
        print("  A: Toggle 3D auto-rotation")
        print("  D: Toggle 4D auto-rotation")
        print("  Space: Toggle simulation")
        print("  C: Cycle color modes")
        print("  V: Toggle charge gradient visualization")
        print("  +/-: Adjust W charge multiplier")
        print("  [/]: Adjust repulsion power")
        print("  1/2: Decrease/Increase damping")
        print("  3/4: Decrease/Increase time step")
        print("  X: Cycle stereoscopic modes (off/side-by-side/anaglyph)")
        print("  ,/.: Adjust eye separation")
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
                        self.camera_pos = [0, 0, -5]
                        self.rotation = [0, 0, 0]
                        self.w_angle = 0.0
                        self.w_position = 0.0
                        print("View reset")
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] += 0.5
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] -= 0.5
                    elif event.key == pygame.K_q:
                        self.charge_strength = max(0.01, self.charge_strength - 0.01)
                        print(f"Charge strength: {self.charge_strength:.3f}")
                    elif event.key == pygame.K_e:
                        self.charge_strength = min(0.5, self.charge_strength + 0.01)
                        print(f"Charge strength: {self.charge_strength:.3f}")
                    elif event.key == pygame.K_a:
                        self.auto_rotate_3d = not self.auto_rotate_3d
                        print(f"3D Auto-rotation: {'ON' if self.auto_rotate_3d else 'OFF'}")
                    elif event.key == pygame.K_d:
                        self.auto_rotate_4d = not self.auto_rotate_4d
                        print(f"4D Auto-rotation: {'ON' if self.auto_rotate_4d else 'OFF'}")
                    elif event.key == pygame.K_SPACE:
                        self.simulate = not self.simulate
                        print(f"Simulation: {'ON' if self.simulate else 'OFF'}")
                    elif event.key == pygame.K_c:
                        self.color_mode = (self.color_mode + 1) % 3
                        modes = ['Charge-based', 'Velocity-based', 'Potential energy']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_v:
                        self.show_charge_gradient = not self.show_charge_gradient
                        print(f"Charge gradient: {'ON' if self.show_charge_gradient else 'OFF'}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.w_charge_multiplier = min(5.0, self.w_charge_multiplier + 0.2)
                        print(f"W charge multiplier: {self.w_charge_multiplier:.1f}")
                    elif event.key == pygame.K_MINUS:
                        self.w_charge_multiplier = max(0.0, self.w_charge_multiplier - 0.2)
                        print(f"W charge multiplier: {self.w_charge_multiplier:.1f}")
                    elif event.key == pygame.K_RIGHTBRACKET:
                        self.repulsion_power = min(4.0, self.repulsion_power + 0.1)
                        print(f"Repulsion power: {self.repulsion_power:.1f}")
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.repulsion_power = max(0.5, self.repulsion_power - 0.1)
                        print(f"Repulsion power: {self.repulsion_power:.1f}")
                    elif event.key == pygame.K_1:
                        self.damping = max(0.8, self.damping - 0.01)
                        print(f"Damping: {self.damping:.3f}")
                    elif event.key == pygame.K_2:
                        self.damping = min(0.99, self.damping + 0.01)
                        print(f"Damping: {self.damping:.3f}")
                    elif event.key == pygame.K_3:
                        self.time_step = max(0.001, self.time_step - 0.001)
                        print(f"Time step: {self.time_step:.3f}")
                    elif event.key == pygame.K_4:
                        self.time_step = min(0.1, self.time_step + 0.001)
                        print(f"Time step: {self.time_step:.3f}")
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
                print(f"W position: {self.w_position:.2f}")
            if keys[pygame.K_g]:
                self.w_position -= 0.02
                print(f"W position: {self.w_position:.2f}")
            
            self.display()
            clock.tick(60)
        
        # Cleanup
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.position_buffer:
            glDeleteBuffers(1, [self.position_buffer])
        if self.velocity_buffer:
            glDeleteBuffers(1, [self.velocity_buffer])
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        if self.compute_program:
            glDeleteProgram(self.compute_program)
        
        pygame.quit()

def main():
    try:
        viewer = GPUElectrostaticHypersphereViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. This requires OpenGL 4.3+ for compute shaders")
        print("2. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("3. Check your graphics drivers are up to date")

if __name__ == "__main__":
    main()