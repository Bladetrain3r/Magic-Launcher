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

class CollatzSphereVisualizerGPU:
    def __init__(self, config_path='collatz_sphere_config.json'):
        # Load configuration
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using defaults")
            self.config = {
                "width": 1280,
                "height": 1280,
                "max_iterations": 320,
                "resolution": 0.015,
                "scale": 40.0,
                "camera": {
                    "initial_position": [0, 0, -10],
                    "initial_rotation": [30, 0, 0],
                    "auto_rotate": {
                        "enabled": False,
                        "speed_x": 0.5,
                        "speed_y": 0.5
                    }
                },
                "color": {
                    "max_power_norm": 64.0,
                    "max_value_norm": 32.0,
                    "value_weight": 0.6,
                    "z_weight": 0.5,
                    "step_weight": 1.0
                }
            }
        
        # Initialize visualization parameters
        self.scale = self.config.get('scale', 40.0)
        self.max_iterations = self.config['max_iterations']
        self.resolution = self.config['resolution']
        
        # Color mapping parameters
        self.color_params = self.config.get('color', {
            'max_power_norm': 64.0,
            'max_value_norm': 32.0,
            'value_weight': 0.6,
            'z_weight': 0.5,
            'step_weight': 1.0
        })
        
        # Camera settings
        self.camera_pos = self.config['camera'].get('initial_position', [0, 0, -10])
        self.rotation = self.config['camera'].get('initial_rotation', [30, 0, 0])
        
        # Auto-rotation settings
        auto_rotate = self.config['camera'].get('auto_rotate', {})
        self.auto_rotate = auto_rotate.get('enabled', False)
        self.auto_rotate_speed = [
            auto_rotate.get('speed_x', 0.5),
            auto_rotate.get('speed_y', 0.5)
        ]
        
        # Pygame and OpenGL setup
        pygame.init()
        display = (self.config.get('width', 1280), self.config.get('height', 1280))
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("GPU Collatz 3D Sphere Visualization")
        
        # Shader program
        self.shader_program = None
        self.vao = None
        self.vbo = None

    def create_shaders(self):
        """Create vertex and fragment shaders for GPU computation"""
        vertex_shader = """
        #version 330 core
        
        layout(location = 0) in vec2 aPos;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float scale;
        uniform float resolution;
        
        out vec3 FragPos;
        out vec3 SphereCoord;
        
        void main()
        {
            // Convert 2D grid to spherical coordinates
            float theta = aPos.x * 2.0 * 3.14159265359;
            float phi = aPos.y * 3.14159265359;
            
            // Convert to cartesian coordinates on unit sphere
            vec3 pos;
            pos.x = sin(phi) * cos(theta);
            pos.y = sin(phi) * sin(theta);
            pos.z = cos(phi);
            
            FragPos = pos;
            SphereCoord = pos;
            
            gl_Position = projection * view * model * vec4(pos, 1.0);
            gl_PointSize = 2.0;
        }
        """
        
        fragment_shader = """
        #version 330 core
        
        in vec3 FragPos;
        in vec3 SphereCoord;
        
        uniform float scale;
        uniform int max_iterations;
        uniform float max_power_norm;
        uniform float max_value_norm;
        uniform float value_weight;
        uniform float z_weight;
        uniform float step_weight;
        
        out vec4 FragColor;
        
        // Check if number is power of two
        bool isPowerOfTwo(float n) {
            if (n <= 0.0) return false;
            int ni = int(n);
            return (ni & (ni - 1)) == 0;
        }
        
        // Calculate Collatz stopping time on GPU
        vec4 calculateCollatz(float n) {
            if (n < 1.0) return vec4(0.0);
            
            float steps = 0.0;
            float current = n;
            float max_value = n;
            float power_two_steps = 0.0;
            bool converged = false;
            
            for (int i = 0; i < max_iterations; i++) {
                if (isPowerOfTwo(current)) {
                    converged = true;
                    power_two_steps = log2(current);
                    break;
                }
                
                if (mod(current, 2.0) < 0.5) {
                    current = floor(current / 2.0);
                } else {
                    current = 3.0 * current + 1.0;
                    max_value = max(max_value, current);
                }
                steps += 1.0;
                
                // Prevent overflow
                if (current > 1e15) break;
            }
            
            return vec4(steps, power_two_steps, max_value, converged ? 1.0 : 0.0);
        }
        
        void main()
        {
            // Map sphere position to number
            float r = length(SphereCoord);
            float base_number = r * pow(2.0, scale);
            
            // Apply some pattern-based adjustments
            float theta = atan(SphereCoord.y, SphereCoord.x);
            float phi = acos(SphereCoord.z / r);
            base_number *= (1.0 + 0.1 * sin(theta * 5.0) * cos(phi * 3.0));
            
            // Calculate Collatz on GPU
            vec4 result = calculateCollatz(base_number);
            
            if (result.w < 0.5) {
                // Not converged - dark color
                FragColor = vec4(0.2, 0.2, 0.2, 1.0);
            } else {
                // Normalize values
                float steps_norm = min(1.0, result.x / float(max_iterations));
                float value_norm = min(1.0, log2(result.z) / max_value_norm);
                float z_norm = (SphereCoord.z + 1.0) / 2.0;
                
                // Color based on Collatz properties
                float r = steps_norm;
                float g = value_norm * 0.5 + z_norm * 0.5;
                float b = (1.0 - steps_norm) * z_norm;
                
                // Add some visual interest
                r = pow(r, 0.8);
                g = pow(g, 0.9);
                b = pow(b, 1.1);
                
                FragColor = vec4(r, g, b, 1.0);
            }
        }
        """
        
        # Compile shaders
        vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        self.shader_program = shaders.compileProgram(vs, fs)

    def create_sphere_mesh(self):
        """Create sphere mesh vertices for GPU processing"""
        vertices = []
        
        # Generate grid of spherical coordinates
        theta_steps = int(2 * np.pi / self.resolution)
        phi_steps = int(np.pi / self.resolution)
        
        for i in range(theta_steps):
            for j in range(phi_steps):
                # Normalized coordinates [0,1]
                u = i / float(theta_steps - 1)
                v = j / float(phi_steps - 1)
                vertices.extend([u, v])
        
        vertices = np.array(vertices, dtype=np.float32)
        
        # Create VAO and VBO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Set vertex attributes
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glBindVertexArray(0)
        
        self.vertex_count = len(vertices) // 2

    def init_gl(self):
        """Initialize OpenGL settings and create GPU resources"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(2.0)
        
        # Create shaders and mesh
        self.create_shaders()
        self.create_sphere_mesh()
        
        print(f"GPU initialization complete. Rendering {self.vertex_count} points.")

    def get_projection_matrix(self):
        """Get perspective projection matrix"""
        width, height = self.config.get('width', 1280), self.config.get('height', 1280)
        fov = 45.0
        aspect = width / height
        near = 0.1
        far = 100.0
        
        # Create perspective matrix
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
        # Translation matrix
        trans = np.eye(4, dtype=np.float32)
        trans[3, :3] = -np.array(self.camera_pos)
        
        # Rotation matrices
        rx = math.radians(self.rotation[0])
        ry = math.radians(self.rotation[1])
        rz = math.radians(self.rotation[2])
        
        # X rotation
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, math.cos(rx), -math.sin(rx), 0],
            [0, math.sin(rx), math.cos(rx), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Y rotation
        rot_y = np.array([
            [math.cos(ry), 0, math.sin(ry), 0],
            [0, 1, 0, 0],
            [-math.sin(ry), 0, math.cos(ry), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Z rotation
        rot_z = np.array([
            [math.cos(rz), -math.sin(rz), 0, 0],
            [math.sin(rz), math.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Combine transformations
        view = trans @ rot_z @ rot_y @ rot_x
        return view

    def display(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Use shader program
        glUseProgram(self.shader_program)
        
        # Set uniforms
        projection_loc = glGetUniformLocation(self.shader_program, "projection")
        view_loc = glGetUniformLocation(self.shader_program, "view")
        model_loc = glGetUniformLocation(self.shader_program, "model")
        scale_loc = glGetUniformLocation(self.shader_program, "scale")
        resolution_loc = glGetUniformLocation(self.shader_program, "resolution")
        max_iter_loc = glGetUniformLocation(self.shader_program, "max_iterations")
        
        # Color parameters
        max_power_loc = glGetUniformLocation(self.shader_program, "max_power_norm")
        max_value_loc = glGetUniformLocation(self.shader_program, "max_value_norm")
        value_weight_loc = glGetUniformLocation(self.shader_program, "value_weight")
        z_weight_loc = glGetUniformLocation(self.shader_program, "z_weight")
        step_weight_loc = glGetUniformLocation(self.shader_program, "step_weight")
        
        # Set matrices
        projection = self.get_projection_matrix()
        view = self.get_view_matrix()
        model = np.eye(4, dtype=np.float32)
        
        glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        
        # Set other uniforms
        glUniform1f(scale_loc, self.scale)
        glUniform1f(resolution_loc, self.resolution)
        glUniform1i(max_iter_loc, self.max_iterations)
        
        glUniform1f(max_power_loc, self.color_params['max_power_norm'])
        glUniform1f(max_value_loc, self.color_params['max_value_norm'])
        glUniform1f(value_weight_loc, self.color_params['value_weight'])
        glUniform1f(z_weight_loc, self.color_params['z_weight'])
        glUniform1f(step_weight_loc, self.color_params['step_weight'])
        
        # Draw
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)
        
        pygame.display.flip()

    def reshape(self, width, height):
        """Handle window reshape"""
        if height == 0:
            height = 1
            
        glViewport(0, 0, width, height)

    def run(self):
        """Main loop"""
        self.init_gl()
        self.reshape(self.config.get('width', 1280), self.config.get('height', 1280))
        
        print("\nGPU-Accelerated Collatz Sphere Visualization")
        print("\nControls:")
        print("  Arrow keys: Rotate")
        print("  Page Up/Down: Zoom in/out")
        print("  A: Toggle auto-rotation")
        print("  R: Reset view")
        print("  +/-: Increase/decrease scale")
        print("  Q or ESC: Quit")
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reset to initial configuration
                        self.camera_pos = self.config['camera'].get('initial_position', [0, 0, -10])
                        self.rotation = self.config['camera'].get('initial_rotation', [30, 0, 0])
                        self.scale = self.config.get('scale', 40.0)
                    elif event.key == pygame.K_PAGEUP:
                        self.camera_pos[2] += 1
                    elif event.key == pygame.K_PAGEDOWN:
                        self.camera_pos[2] -= 1
                    elif event.key == pygame.K_a:
                        self.auto_rotate = not self.auto_rotate
                        print(f"Auto-rotation: {'ON' if self.auto_rotate else 'OFF'}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.scale += 2.0
                        print(f"Scale: {self.scale}")
                    elif event.key == pygame.K_MINUS:
                        self.scale = max(1.0, self.scale - 2.0)
                        print(f"Scale: {self.scale}")
            
            # Handle rotation
            if self.auto_rotate:
                self.rotation[0] += self.auto_rotate_speed[0]
                self.rotation[1] += self.auto_rotate_speed[1]
            else:
                keys = pygame.key.get_pressed()
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
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader_program)
        
        pygame.quit()

def create_default_config():
    """Create a default configuration file if it doesn't exist."""
    default_config = {
        "width": 1280,
        "height": 1280,
        "max_iterations": 320,
        "resolution": 0.015,
        "scale": 40.0,
        "camera": {
            "initial_position": [0, 0, -10],
            "initial_rotation": [30, 0, 0],
            "auto_rotate": {
                "enabled": False,
                "speed_x": 0.5,
                "speed_y": 0.5
            }
        },
        "color": {
            "max_power_norm": 64.0,
            "max_value_norm": 32.0,
            "value_weight": 0.6,
            "z_weight": 0.5,
            "step_weight": 1.0
        }
    }
    
    config_path = 'collatz_sphere_config.json'
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default configuration file: {config_path}")

def main():
    # Create default config if it doesn't exist
    create_default_config()
    
    # Check OpenGL version
    try:
        # Initialize and run the GPU visualization
        viz = CollatzSphereVisualizerGPU()
        viz.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This GPU version requires OpenGL 3.3+ and PyOpenGL with shader support.")
        print("If you encounter issues, ensure your graphics drivers are up to date.")

if __name__ == "__main__":
    main()