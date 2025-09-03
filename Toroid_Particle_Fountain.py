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

class ChargedToroidParticleSystem:
    def __init__(self):
        # Toroid parameters
        self.major_radius = 1.2
        self.minor_radius = 1.0
        self.toroid_points = 500000
        self.toroid_charge = -1.0  # Negative charge on toroid
        self.distribution = 'Poisson'  # Distribution method
        
        # Particle parameters
        self.max_particles = 10000
        self.active_particles = 0
        self.particle_charge = 1.0  # Positive charge on particles
        self.emission_rate = 500  # Particles per emission
        self.emission_velocity = 0.5
        self.emission_spread = 0.2
        self.emit_from_hole = True  # Emit from center hole vs random positions
        
        # Physics parameters
        self.coulomb_constant = 0.1
        self.damping = 0.98
        self.time_step = 0.01
        self.simulate = True
        self.collision_radius = 0.05
        self.particle_lifetime = 500  # Frames
        
        # 4D parameters
        self.w_angle = 0.0
        self.w_position = 0.0
        self.xw_rotation_speed = 0.3
        self.yz_rotation_speed = 0.2
        self.zw_rotation_speed = 0.15
        self.xy_rotation_speed = 0.25
        self.auto_rotate_4d = False
        
        # 3D camera settings
        self.camera_pos = [0, 0, 6]
        self.rotation = [0, 0, 0]
        self.auto_rotate_3d = False
        self.auto_rotate_speed = [0.5, 0.5]
        
        # Display settings
        self.width = 1920
        self.height = 1280
        self.base_point_size = 1.0
        self.particle_size = 3.0
        self.color_mode = 0
        self.show_field_lines = True
        self.show_trails = True
        self.trail_length = 20
        
        # Stereoscopic settings
        self.stereoscopic_mode = 0
        self.eye_separation = 0.15
        self.convergence_distance = 6.0
        
        # OpenGL objects
        self.shader_program = None
        self.compute_shader = None
        self.toroid_vao = None
        self.particle_vao = None
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
        pygame.display.set_caption("4D Charged Toroid with Particle Emission")
        
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
        except Exception as e:
            print(f"OpenGL context verification failed: {e}")
            raise

    def create_shaders(self):
        """Create compute and rendering shaders"""
        # Compute shader for particle physics
        compute_shader_source = """
        #version 430 core
        
        layout(local_size_x = 64) in;
        
        struct Particle {
            vec4 position;
            vec4 velocity;
            float life;
            float charge;
            float pad1;
            float pad2;
        };
        
        layout(std430, binding = 0) buffer ToroidBuffer {
            vec4 toroid_points[];
        };
        
        layout(std430, binding = 1) buffer ParticleBuffer {
            Particle particles[];
        };
        
        uniform uint toroid_point_count;
        uniform uint particle_count;
        uniform float toroid_charge;
        uniform float coulomb_constant;
        uniform float damping;
        uniform float time_step;
        uniform float w_position;
        uniform float collision_radius;
        uniform float major_radius;
        uniform float minor_radius;
        
        void main() {
            uint idx = gl_GlobalInvocationID.x;
            if (idx >= particle_count) return;
            
            Particle p = particles[idx];
            if (p.life <= 0.0) return;
            
            vec4 force = vec4(0.0);
            
            // Calculate forces from toroid points
            // Sample a subset for performance
            uint step = max(1u, toroid_point_count / 500u);
            for (uint i = 0; i < toroid_point_count; i += step) {
                vec4 toroid_pos = toroid_points[i];
                vec4 diff = p.position - toroid_pos;
                float dist_sq = dot(diff, diff);
                
                if (dist_sq < 0.001) dist_sq = 0.001;
                
                float dist = sqrt(dist_sq);
                float force_magnitude = coulomb_constant * p.charge * toroid_charge / dist_sq;
                
                // Opposite charges attract
                force -= normalize(diff) * force_magnitude;
            }
            
            // 4D "gravity" towards toroid center (helps contain particles)
            vec4 center_force = -p.position * 0.1;
            force += center_force;
            
            // Update velocity and position
            p.velocity = p.velocity * damping + force * time_step;
            p.position += p.velocity * time_step;
            
            // Check for collision with toroid surface
            // For a proper 4D toroid (Clifford torus):
            // Distance from first circle center in XY
            float dist_xy = sqrt(p.position.x * p.position.x + p.position.y * p.position.y);
            // Distance from second circle center in ZW
            float dist_zw = sqrt(p.position.z * p.position.z + p.position.w * p.position.w);
            
            // Check if near toroid surface
            bool near_major = abs(dist_xy - major_radius) < collision_radius;
            bool near_minor = abs(dist_zw - minor_radius) < collision_radius;
            
            if (near_major && near_minor) {
                // Collision! Absorb the particle
                p.life = 0.0;
            }
            
            // Update life
            p.life -= 1.0;
            
            // Store updated particle
            particles[idx] = p;
        }
        """
        
        # Vertex shader for rendering
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in vec4 position;
        layout(location = 1) in float point_type;  // 0 = toroid, 1+ = particle
        layout(location = 2) in float life;
        
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
        uniform float base_point_size;
        uniform float particle_size;
        
        out vec3 FragPos;
        out vec4 WorldPos4D;
        out float PointType;
        out float Life;
        out float WCoord;
        
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
            
            // Store W coordinate
            WCoord = point4d.w;
            
            // Stereographic projection
            float projection_factor = 2.5 / (2.5 - point4d.w * 0.4);
            
            vec3 point3d;
            point3d.x = point4d.x * projection_factor;
            point3d.y = point4d.y * projection_factor;
            point3d.z = point4d.z * projection_factor;
            
            return point3d;
        }
        
        void main() {
            WorldPos4D = position;
            PointType = point_type;
            Life = life;
            
            vec3 pos = project_4d_to_3d(position);
            FragPos = pos;
            
            gl_Position = projection * view * model * vec4(pos, 1.0);
            
            // Point size based on type and life
            if (point_type == 0.0) {
                // Toroid point
                gl_PointSize = base_point_size;
            } else {
                // Particle - size based on life
                float life_factor = life / 500.0;  // Assuming max life of 500
                gl_PointSize = particle_size * (0.5 + 0.5 * life_factor);
            }
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec4 WorldPos4D;
        in float PointType;
        in float Life;
        in float WCoord;
        
        uniform float time;
        uniform int color_mode;
        
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
        
        void main() {
            vec3 color;
            float alpha = 1.0;
            
            if (PointType == 0.0) {
                // Toroid point - negative charge (blue-ish)
                if (color_mode == 0) {
                    // Electric field visualization
                    float field_strength = abs(WCoord);
                    color = mix(vec3(0.0, 0.2, 0.8), vec3(0.0, 0.5, 1.0), field_strength);
                } else {
                    // Static blue for negative charge
                    color = vec3(0.1, 0.3, 0.9);
                }
                
                // Pulsing effect
                color *= (0.8 + 0.2 * sin(time * 0.003));
                
            } else {
                // Particle - positive charge (red/orange/yellow)
                float life_factor = Life / 500.0;
                
                if (color_mode == 0) {
                    // Life-based coloring
                    float hue = 60.0 * life_factor;  // Yellow to red
                    color = hsv_to_rgb(vec3(hue, 0.9, 0.9));
                } else {
                    // Velocity-based coloring
                    float speed = length(WorldPos4D);
                    float hue = 120.0 - 120.0 * min(speed * 0.5, 1.0);  // Green to red
                    color = hsv_to_rgb(vec3(hue, 0.8, 0.9));
                }
                
                // Fade out as particle dies
                alpha = life_factor;
                
                // Add glow effect
                color += vec3(0.2, 0.1, 0.0) * life_factor;
            }
            
            // Distance fade
            float dist = length(FragPos);
            float fade = 1.0 - smoothstep(8.0, 20.0, dist);
            
            FragColor = vec4(color * fade, alpha * fade);
        }
        """
        
        try:
            # Compile compute shader
            self.compute_shader = glCreateShader(GL_COMPUTE_SHADER)
            glShaderSource(self.compute_shader, compute_shader_source)
            glCompileShader(self.compute_shader)
            
            if not glGetShaderiv(self.compute_shader, GL_COMPILE_STATUS):
                error = glGetShaderInfoLog(self.compute_shader).decode()
                raise RuntimeError(f"Compute shader compilation error: {error}")
            
            self.compute_program = glCreateProgram()
            glAttachShader(self.compute_program, self.compute_shader)
            glLinkProgram(self.compute_program)
            
            if not glGetProgramiv(self.compute_program, GL_LINK_STATUS):
                error = glGetProgramInfoLog(self.compute_program).decode()
                raise RuntimeError(f"Compute program linking error: {error}")
            
            # Compile rendering shaders
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            
            print("Charged toroid particle shaders compiled successfully!")
            
        except Exception as e:
            print(f"Shader compilation error: {e}")
            raise

    def create_buffers(self):
        """Create GPU buffers for toroid and particles"""
        # Generate toroid points based on selected distribution
        toroid_positions = []
        n = self.toroid_points
        golden_ratio = (1 + np.sqrt(5)) / 2
        
        if self.distribution == 'spherical_fibonacci':
            # Spherical fibonacci distribution
            for i in range(n):
                angle1 = 2 * np.pi * np.fmod(i * golden_ratio, 1)
                angle2 = 2 * np.pi * np.fmod(i / golden_ratio, 1)
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        elif self.distribution == 'lissajous':
            # Lissajous curves - creates beautiful patterns
            freq1, freq2 = 3, 4
            phase = np.pi / 4
            
            for i in range(n):
                t = i / n * 2 * np.pi
                angle1 = freq1 * t
                angle2 = freq2 * t + phase
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        elif self.distribution == 'hopf':
            # Hopf fibration-inspired
            for i in range(n):
                t1 = i / n
                t2 = np.fmod(i * golden_ratio, 1)
                
                eta = t1 * np.pi
                xi1 = t2 * 2 * np.pi
                xi2 = np.fmod(i * golden_ratio * golden_ratio, 1) * 2 * np.pi
                
                angle1 = xi1
                angle2 = xi2 + eta
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        elif self.distribution == 'spiral':
            # Double spiral
            spiral_turns = 8
            
            for i in range(n):
                t = i / n
                angle1 = t * 2 * np.pi
                angle2 = t * 2 * np.pi * spiral_turns
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        elif self.distribution == 'grid':
            # Uniform grid
            grid_size = int(np.sqrt(n))
            
            for i in range(n):
                i1 = i % grid_size
                i2 = i // grid_size
                
                angle1 = 2 * np.pi * i1 / grid_size
                angle2 = 2 * np.pi * i2 / grid_size
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        elif self.distribution == 'poisson':
            # Poisson disk approximation
            cell_size = int(np.sqrt(n))
            
            for i in range(n):
                cell_x = i % cell_size
                cell_y = i // cell_size
                
                # Add jitter
                jitter1 = np.random.random()
                jitter2 = np.random.random()
                
                angle1 = 2 * np.pi * (cell_x + jitter1) / cell_size
                angle2 = 2 * np.pi * (cell_y + jitter2) / cell_size
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
                
        else:  # random
            # Pure random
            for i in range(n):
                angle1 = np.random.uniform(0, 2 * np.pi)
                angle2 = np.random.uniform(0, 2 * np.pi)
                
                x = self.major_radius * np.cos(angle1)
                y = self.major_radius * np.sin(angle1)
                z = self.minor_radius * np.cos(angle2)
                w = self.minor_radius * np.sin(angle2)
                
                toroid_positions.append([x, y, z, w])
        
        toroid_positions = np.array(toroid_positions, dtype=np.float32)
        
        # Create toroid buffer (SSBO)
        self.toroid_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.toroid_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, toroid_positions.nbytes, toroid_positions, GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.toroid_buffer)
        
        # Create particle buffer
        # Particle structure: position(4), velocity(4), life(1), charge(1), pad(2) = 12 floats
        particle_data = np.zeros((self.max_particles, 12), dtype=np.float32)
        
        self.particle_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.particle_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, particle_data.nbytes, particle_data, GL_DYNAMIC_COPY)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.particle_buffer)
        
        # Create combined vertex buffer for rendering
        # Format: position(4), type(1), life(1) = 6 floats per vertex
        total_vertices = self.toroid_points + self.max_particles
        vertex_data = np.zeros((total_vertices, 6), dtype=np.float32)
        
        # Fill toroid data
        vertex_data[:self.toroid_points, :4] = toroid_positions
        vertex_data[:self.toroid_points, 4] = 0.0  # Type 0 = toroid
        vertex_data[:self.toroid_points, 5] = 1.0  # Life = 1 (always alive)
        
        # Create VAO for rendering
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_DYNAMIC_DRAW)
        
        # Position attribute
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Type attribute
        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(4 * 4))
        glEnableVertexAttribArray(1)
        
        # Life attribute
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(5 * 4))
        glEnableVertexAttribArray(2)
        
        glBindVertexArray(0)
        
        self.vertex_count = total_vertices
        print(f"Created buffers: {self.toroid_points} toroid points, {self.max_particles} max particles")

    def emit_particles(self):
        """Emit new particles through the toroid hole"""
        if self.active_particles + self.emission_rate > self.max_particles:
            return
        
        # Read current particle data
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.particle_buffer)
        particle_data = np.frombuffer(
            glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.max_particles * 12 * 4),
            dtype=np.float32
        ).reshape((self.max_particles, 12))
        
        if self.emit_from_hole:
            # Emit particles through the toroid hole
            for i in range(self.emission_rate):
                idx = self.active_particles + i
                if idx >= self.max_particles:
                    break
                
                # Random angle around the hole
                angle = np.random.uniform(0, 2 * np.pi)
                radius = np.random.uniform(0, 0.3)  # Small radius in hole
                
                # Position: in the ZW plane (the "hole" of the XY major circle)
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                z = 0.0
                w = 0.0
                
                # Velocity: random direction with bias along the hole axis
                vx = np.random.normal(0, self.emission_spread)
                vy = np.random.normal(0, self.emission_spread)
                vz = self.emission_velocity + np.random.normal(0, self.emission_spread * 0.5)
                vw = np.random.normal(0, self.emission_spread * 0.5)
                
                # Set particle data
                particle_data[idx, 0:4] = [x, y, z, w]  # Position
                particle_data[idx, 4:8] = [vx, vy, vz, vw]  # Velocity
                particle_data[idx, 8] = self.particle_lifetime  # Life
                particle_data[idx, 9] = self.particle_charge  # Charge
        else:
            # Emit particles from random positions near toroid
            for i in range(self.emission_rate):
                idx = self.active_particles + i
                if idx >= self.max_particles:
                    break
                
                # Random position outside toroid
                angle1 = np.random.uniform(0, 2 * np.pi)
                angle2 = np.random.uniform(0, 2 * np.pi)
                
                # Start slightly outside the toroid surface
                distance = 1.2
                x = (self.major_radius + distance) * np.cos(angle1)
                y = (self.major_radius + distance) * np.sin(angle1)
                z = (self.minor_radius + distance) * np.cos(angle2)
                w = (self.minor_radius + distance) * np.sin(angle2)
                
                # Velocity towards toroid center
                vel_magnitude = self.emission_velocity
                vx = -x * vel_magnitude / np.sqrt(x*x + y*y + z*z + w*w)
                vy = -y * vel_magnitude / np.sqrt(x*x + y*y + z*z + w*w)
                vz = -z * vel_magnitude / np.sqrt(x*x + y*y + z*z + w*w)
                vw = -w * vel_magnitude / np.sqrt(x*x + y*y + z*z + w*w)
                
                # Add some randomness
                vx += np.random.normal(0, self.emission_spread)
                vy += np.random.normal(0, self.emission_spread)
                vz += np.random.normal(0, self.emission_spread)
                vw += np.random.normal(0, self.emission_spread)
                
                # Set particle data
                particle_data[idx, 0:4] = [x, y, z, w]  # Position
                particle_data[idx, 4:8] = [vx, vy, vz, vw]  # Velocity
                particle_data[idx, 8] = self.particle_lifetime  # Life
                particle_data[idx, 9] = self.particle_charge  # Charge
        
        # Upload updated data
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, particle_data.nbytes, particle_data)
        
        self.active_particles = min(self.active_particles + self.emission_rate, self.max_particles)

    def update_vertex_buffer(self):
        """Update the vertex buffer with current particle positions"""
        # Read particle data from compute shader output
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.particle_buffer)
        particle_data = np.frombuffer(
            glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.max_particles * 12 * 4),
            dtype=np.float32
        ).reshape((self.max_particles, 12))
        
        # Update vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        
        # Update only particle vertices (after toroid points)
        offset = self.toroid_points * 6 * 4  # Offset in bytes
        
        # Create vertex data for particles
        particle_vertices = np.zeros((self.max_particles, 6), dtype=np.float32)
        particle_vertices[:, :4] = particle_data[:, :4]  # Position
        particle_vertices[:, 4] = 1.0  # Type 1 = particle
        particle_vertices[:, 5] = particle_data[:, 8]  # Life
        
        glBufferSubData(GL_ARRAY_BUFFER, offset, particle_vertices.nbytes, particle_vertices)

    def run_compute_shader(self):
        """Execute the compute shader for particle physics"""
        if not self.simulate:
            return
        
        glUseProgram(self.compute_program)
        
        # Set uniforms
        glUniform1ui(glGetUniformLocation(self.compute_program, "toroid_point_count"), self.toroid_points)
        glUniform1ui(glGetUniformLocation(self.compute_program, "particle_count"), self.active_particles)
        glUniform1f(glGetUniformLocation(self.compute_program, "toroid_charge"), self.toroid_charge)
        glUniform1f(glGetUniformLocation(self.compute_program, "coulomb_constant"), self.coulomb_constant)
        glUniform1f(glGetUniformLocation(self.compute_program, "damping"), self.damping)
        glUniform1f(glGetUniformLocation(self.compute_program, "time_step"), self.time_step)
        glUniform1f(glGetUniformLocation(self.compute_program, "w_position"), self.w_position)
        glUniform1f(glGetUniformLocation(self.compute_program, "collision_radius"), self.collision_radius)
        glUniform1f(glGetUniformLocation(self.compute_program, "major_radius"), self.major_radius)
        glUniform1f(glGetUniformLocation(self.compute_program, "minor_radius"), self.minor_radius)
        
        # Dispatch compute shader
        work_groups = (self.active_particles + 63) // 64
        if work_groups > 0:
            glDispatchCompute(work_groups, 1, 1)
        
        # Memory barrier
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT | GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)

    def init_gl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.0, 0.0, 0.02, 1.0)
        
        # Enable point size and blending
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Create shaders and buffers
        self.create_shaders()
        self.create_buffers()
        
        print("GPU initialization complete")

    def get_projection_matrix_stereo(self, width, height, eye_offset):
        """Get perspective projection matrix with stereo offset"""
        fov = 45.0
        aspect = width / height
        near = 0.1
        far = 50.0
        
        top = near * math.tan(math.radians(fov) / 2.0)
        bottom = -top
        
        frustum_shift = -(eye_offset * near) / self.convergence_distance
        left = -aspect * top + frustum_shift
        right = aspect * top + frustum_shift
        
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
        translation = np.eye(4, dtype=np.float32)
        translation[0, 3] = -(self.camera_pos[0] + eye_offset)
        translation[1, 3] = -self.camera_pos[1]
        translation[2, 3] = -self.camera_pos[2]
        
        rx = math.radians(self.rotation[0])
        ry = math.radians(self.rotation[1])
        rz = math.radians(self.rotation[2])
        
        rot_x = np.eye(4, dtype=np.float32)
        rot_x[1, 1] = math.cos(rx)
        rot_x[1, 2] = -math.sin(rx)
        rot_x[2, 1] = math.sin(rx)
        rot_x[2, 2] = math.cos(rx)
        
        rot_y = np.eye(4, dtype=np.float32)
        rot_y[0, 0] = math.cos(ry)
        rot_y[0, 2] = math.sin(ry)
        rot_y[2, 0] = -math.sin(ry)
        rot_y[2, 2] = math.cos(ry)
        
        rot_z = np.eye(4, dtype=np.float32)
        rot_z[0, 0] = math.cos(rz)
        rot_z[0, 1] = -math.sin(rz)
        rot_z[1, 0] = math.sin(rz)
        rot_z[1, 1] = math.cos(rz)
        
        view = translation @ rot_x @ rot_y @ rot_z
        return view

    def render_eye(self, x, y, width, height, eye_offset):
        """Render from a single eye perspective"""
        glUseProgram(self.shader_program)
        
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
            'base_point_size': glGetUniformLocation(self.shader_program, "base_point_size"),
            'particle_size': glGetUniformLocation(self.shader_program, "particle_size"),
            'color_mode': glGetUniformLocation(self.shader_program, "color_mode")
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
        glUniform1f(uniforms['w_angle'], self.w_angle)
        glUniform1f(uniforms['w_position'], self.w_position)
        glUniform1f(uniforms['xw_speed'], self.xw_rotation_speed)
        glUniform1f(uniforms['yz_speed'], self.yz_rotation_speed)
        glUniform1f(uniforms['zw_speed'], self.zw_rotation_speed)
        glUniform1f(uniforms['xy_speed'], self.xy_rotation_speed)
        glUniform1f(uniforms['base_point_size'], self.base_point_size)
        glUniform1f(uniforms['particle_size'], self.particle_size)
        glUniform1i(uniforms['color_mode'], self.color_mode)
        
        # Draw all points
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)

    def display(self):
        """Render the scene"""
        # Run physics simulation
        self.run_compute_shader()
        
        # Update vertex buffer with new particle positions
        self.update_vertex_buffer()
        
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.stereoscopic_mode == 0:
            # Normal rendering
            self.render_eye(0, 0, self.width, self.height, 0.0)
        elif self.stereoscopic_mode == 1:
            # Side-by-side stereoscopic
            glViewport(0, 0, self.width // 2, self.height)
            self.render_eye(0, 0, self.width // 2, self.height, -self.eye_separation)
            
            glViewport(self.width // 2, 0, self.width // 2, self.height)
            self.render_eye(self.width // 2, 0, self.width // 2, self.height, self.eye_separation)
            
            glViewport(0, 0, self.width, self.height)
        elif self.stereoscopic_mode == 2:
            # Anaglyph stereoscopic
            glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
            self.render_eye(0, 0, self.width, self.height, -self.eye_separation)
            
            glClear(GL_DEPTH_BUFFER_BIT)
            
            glColorMask(GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE)
            self.render_eye(0, 0, self.width, self.height, self.eye_separation)
            
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        
        pygame.display.flip()

    def run(self):
        """Main loop"""
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\n4D Charged Toroid with Particle Emission")
        print("\nPhysics:")
        print("  - Negatively charged toroid attracts positive particles")
        print("  - Particles are emitted through the toroid hole")
        print("  - Particles spiral and are absorbed on collision")
        print("\nControls:")
        print("  Arrow keys: Rotate 3D view")
        print("  Page Up/Down: Zoom in/out")
        print("  W/S: Rotate in 4D (W dimension)")
        print("  T/G: Pan along W axis")
        print("  Space: Emit particle burst")
        print("  H: Toggle emission mode (hole vs outside)")
        print("  P: Toggle physics simulation")
        print("  A: Toggle 3D auto-rotation")
        print("  D: Toggle 4D auto-rotation")
        print("  C: Cycle color modes")
        print("  Q/E: Adjust toroid charge")
        print("  Z/X: Adjust particle charge")
        print("  +/-: Adjust Coulomb constant")
        print("  [/]: Adjust emission velocity")
        print("  1/2: Adjust damping")
        print("  V: Cycle stereoscopic modes")
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
                        # Reset
                        self.camera_pos = [0, 0, 6]
                        self.rotation = [0, 0, 0]
                        self.w_angle = 0.0
                        self.w_position = 0.0
                        self.active_particles = 0
                        print("Reset")
                    elif event.key == pygame.K_SPACE:
                        self.emit_particles()
                        print(f"Emitted particles! Active: {self.active_particles}")
                    elif event.key == pygame.K_h:
                        self.emit_from_hole = not self.emit_from_hole
                        mode = "hole" if self.emit_from_hole else "outside"
                        print(f"Emission mode: {mode}")
                    elif event.key == pygame.K_p:
                        self.simulate = not self.simulate
                        print(f"Physics: {'ON' if self.simulate else 'OFF'}")
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] += 0.5
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] -= 0.5
                    elif event.key == pygame.K_a:
                        self.auto_rotate_3d = not self.auto_rotate_3d
                        print(f"3D Auto-rotation: {'ON' if self.auto_rotate_3d else 'OFF'}")
                    elif event.key == pygame.K_d:
                        self.auto_rotate_4d = not self.auto_rotate_4d
                        print(f"4D Auto-rotation: {'ON' if self.auto_rotate_4d else 'OFF'}")
                    elif event.key == pygame.K_c:
                        self.color_mode = (self.color_mode + 1) % 2
                        modes = ['Life-based', 'Velocity-based']
                        print(f"Color mode: {modes[self.color_mode]}")
                    elif event.key == pygame.K_q:
                        self.toroid_charge = max(-2.0, self.toroid_charge - 0.1)
                        print(f"Toroid charge: {self.toroid_charge:.1f}")
                    elif event.key == pygame.K_e:
                        self.toroid_charge = min(-0.1, self.toroid_charge + 0.1)
                        print(f"Toroid charge: {self.toroid_charge:.1f}")
                    elif event.key == pygame.K_z:
                        self.particle_charge = max(0.1, self.particle_charge - 0.1)
                        print(f"Particle charge: {self.particle_charge:.1f}")
                    elif event.key == pygame.K_x:
                        self.particle_charge = min(2.0, self.particle_charge + 0.1)
                        print(f"Particle charge: {self.particle_charge:.1f}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.coulomb_constant = min(1.0, self.coulomb_constant + 0.01)
                        print(f"Coulomb constant: {self.coulomb_constant:.2f}")
                    elif event.key == pygame.K_MINUS:
                        self.coulomb_constant = max(0.01, self.coulomb_constant - 0.01)
                        print(f"Coulomb constant: {self.coulomb_constant:.2f}")
                    elif event.key == pygame.K_RIGHTBRACKET:
                        self.emission_velocity = min(2.0, self.emission_velocity + 0.1)
                        print(f"Emission velocity: {self.emission_velocity:.1f}")
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.emission_velocity = max(0.1, self.emission_velocity - 0.1)
                        print(f"Emission velocity: {self.emission_velocity:.1f}")
                    elif event.key == pygame.K_1:
                        self.damping = max(0.8, self.damping - 0.01)
                        print(f"Damping: {self.damping:.2f}")
                    elif event.key == pygame.K_2:
                        self.damping = min(0.99, self.damping + 0.01)
                        print(f"Damping: {self.damping:.2f}")
                    elif event.key == pygame.K_v:
                        self.stereoscopic_mode = (self.stereoscopic_mode + 1) % 3
                        modes = ['Off', 'Side-by-side', 'Anaglyph']
                        print(f"Stereoscopic: {modes[self.stereoscopic_mode]}")
                    elif event.key == pygame.K_COMMA:
                        self.eye_separation = max(0.05, self.eye_separation - 0.05)
                        print(f"Eye separation: {self.eye_separation:.2f}")
                    elif event.key == pygame.K_PERIOD:
                        self.eye_separation = min(1.0, self.eye_separation + 0.05)
                        print(f"Eye separation: {self.eye_separation:.2f}")
            
            # Handle continuous rotation
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
            
            # W-dimension controls
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
        if hasattr(self, 'toroid_buffer'):
            glDeleteBuffers(1, [self.toroid_buffer])
        if hasattr(self, 'particle_buffer'):
            glDeleteBuffers(1, [self.particle_buffer])
        if hasattr(self, 'vertex_buffer'):
            glDeleteBuffers(1, [self.vertex_buffer])
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        if hasattr(self, 'compute_program'):
            glDeleteProgram(self.compute_program)
        
        pygame.quit()

def main():
    try:
        system = ChargedToroidParticleSystem()
        system.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. This requires OpenGL 4.3+ for compute shaders")
        print("2. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("3. Check your graphics drivers are up to date")

if __name__ == "__main__":
    main()