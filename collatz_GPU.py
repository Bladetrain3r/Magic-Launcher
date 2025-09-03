#!/usr/bin/env python3
"""
Collatz Live Sphere Viewer - Interactive GPU-accelerated visualization
Based on the clean patterns from the 4D toroid viewer
Explores Collatz sequence patterns mapped onto a sphere in real-time
"""

import math
import sys
import time
import ctypes
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GL import shaders

class CollatzSphereViewer:
    def __init__(self):
        # Sphere parameters
        self.radius = 1.0
        self.point_count = 50_000
        self.scale_exponent = 20.0  # For mapping position to number
        self.max_iterations = 320
        
        # Display settings
        self.width = 1600
        self.height = 900
        self.point_size = 2.0
        self.color_mode = 0  # 0: steps, 1: max_value, 2: convergence_speed
        
        # Camera settings
        self.camera_pos = [0.0, 0.0, 3.0]
        self.rotation = [0.0, 0.0]  # X, Y rotation
        self.auto_rotate = False
        self.rotate_speed = [0.3, 0.5]
        
        # GL objects
        self.shader_program = None
        self.vao = None
        self.vbo = None
        self.vertex_count = 0
        self.uniforms = {}
        
        # FPS tracking
        self._frame_count = 0
        self._last_fps_t = time.time()
        self._fps = 0.0

    def initialize_pygame_and_opengl(self):
        """Initialize Pygame and OpenGL context with MSAA"""
        pygame.init()
        
        # GL attributes
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Collatz Sphere - Interactive")
        
        pygame.display.flip()
        time.sleep(0.05)
        
        version = glGetString(GL_VERSION)
        if not version:
            raise RuntimeError("Failed to create OpenGL context")
        
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"Renderer: {glGetString(GL_RENDERER).decode()}")

    def create_shaders(self):
        """Create and compile shaders with Collatz calculation on GPU"""
        vertex_shader = r"""
        #version 330 core
        layout(location = 0) in float index;
        
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float point_count;
        uniform float scale_exponent;
        uniform int max_iterations;
        uniform float point_size;
        uniform float rotation_x;
        uniform float rotation_y;
        
        out vec3 FragPos;
        out float Steps;
        out float MaxValue;
        out float ConvergenceSpeed;
        out float Converged;
        
        const float PI = 3.14159265359;
        const float PHI = 1.61803398875;
        
        // Generate sphere point using Fibonacci lattice (improved distribution)
        vec3 generate_sphere_point(float idx) {
            float n = point_count;
            
            // Better distribution for high point counts
            float theta = 2.0 * PI * fract(idx * PHI);
            float phi = acos(1.0 - 2.0 * (idx + 0.5) / n);  // Added 0.5 offset for better poles
            
            float sin_phi = sin(phi);
            vec3 p;
            p.x = cos(theta) * sin_phi;
            p.y = sin(theta) * sin_phi;
            p.z = cos(phi);
            
            return normalize(p);  // Ensure unit sphere
        }
        
        // Map 3D position to Collatz number (with overflow protection)
        int position_to_number(vec3 pos) {
            float r = length(pos);
            
            // Use logarithmic scaling to prevent overflow
            float log_n = r * scale_exponent * 0.693147; // ln(2) = 0.693147
            
            // Cap at reasonable maximum to prevent overflow
            if (log_n > 20.0) {
                log_n = 20.0; // e^20 ≈ 485 million
            }
            
            int n = int(exp(log_n));
            
            // Apply pattern-based adjustments (safely)
            if (n > 0 && n < 1000000000) {
                if ((n & 0x5) == 0x5) n = min(int(n * 1.1), 1000000000);
                if ((n & 0x7) == 0x7) n = int(n * 0.9);
            }
            
            return max(1, min(n, 1000000000));
        }
        
        // Check if number is power of two
        bool is_power_of_two(int n) {
            return n > 0 && (n & (n - 1)) == 0;
        }
        
        // Calculate Collatz properties (with better overflow handling)
        void calculate_collatz(int n) {
            Steps = 0.0;
            MaxValue = float(n);
            ConvergenceSpeed = 0.0;
            Converged = 0.0;
            
            int current = n;
            int first_decrease_step = -1;
            int loop_guard = 0;
            
            for (int i = 0; i < max_iterations; i++) {
                // Additional loop detection
                loop_guard++;
                if (loop_guard > 500) break;
                
                if (is_power_of_two(current)) {
                    Converged = 1.0;
                    Steps = float(i);
                    if (first_decrease_step > 0) {
                        ConvergenceSpeed = float(first_decrease_step) / Steps;
                    }
                    break;
                }
                
                // Check for overflow before calculation
                if (current % 2 == 0) {
                    current = current / 2;
                } else {
                    // Check if 3n+1 would overflow
                    if (current > 333333333) {  // (1000000000 - 1) / 3
                        break;  // Would overflow, stop here
                    }
                    current = 3 * current + 1;
                }
                
                if (float(current) > MaxValue) {
                    MaxValue = float(current);
                }
                
                if (first_decrease_step < 0 && current < n) {
                    first_decrease_step = i;
                }
                
                // Safety checks
                if (current < 1) break;
                if (current > 1000000000) break;
            }
        }
        
        void main() {
            vec3 sphere_pos = generate_sphere_point(index);
            
            // Apply rotation to sphere
            float rx = rotation_x;
            float ry = rotation_y;
            
            // Rotation around X axis
            mat3 rot_x = mat3(
                1, 0, 0,
                0, cos(rx), -sin(rx),
                0, sin(rx), cos(rx)
            );
            
            // Rotation around Y axis
            mat3 rot_y = mat3(
                cos(ry), 0, sin(ry),
                0, 1, 0,
                -sin(ry), 0, cos(ry)
            );
            
            sphere_pos = rot_y * rot_x * sphere_pos;
            FragPos = sphere_pos;
            
            // Calculate Collatz properties
            int n = position_to_number(sphere_pos);
            calculate_collatz(n);
            
            // Only show converged points
            if (Converged > 0.5) {
                gl_Position = projection * view * model * vec4(sphere_pos, 1.0);
                gl_PointSize = point_size * (1.0 + (100.0 - Steps) * 0.01);
            } else {
                gl_Position = vec4(0, 0, -100, 1);  // Hide non-converged points
                gl_PointSize = 0.0;
            }
        }
        """
        
        fragment_shader = r"""
        #version 330 core
        in vec3 FragPos;
        in float Steps;
        in float MaxValue;
        in float ConvergenceSpeed;
        in float Converged;
        
        uniform int color_mode;
        uniform int max_iterations;
        
        out vec4 FragColor;
        
        vec3 hsv_to_rgb(vec3 hsv) {
            float h = hsv.x, s = hsv.y, v = hsv.z;
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
            if (Converged < 0.5) discard;
            
            vec3 color;
            
            if (color_mode == 0) {
                // Color by steps to convergence
                float steps_norm = Steps / float(max_iterations);
                float hue = (1.0 - steps_norm) * 240.0;  // Blue to red
                color = hsv_to_rgb(vec3(hue, 0.8, 0.9));
                
            } else if (color_mode == 1) {
                // Color by maximum value reached
                float max_norm = log(MaxValue) / 20.0;  // Log scale
                float hue = max_norm * 300.0;
                color = hsv_to_rgb(vec3(hue, 0.7, 0.8));
                
            } else {
                // Color by convergence speed
                float hue = ConvergenceSpeed * 360.0;
                color = hsv_to_rgb(vec3(hue, 0.9, 0.85));
            }
            
            // Add depth shading
            float depth = gl_FragCoord.z;
            color *= (1.2 - depth * 0.2);
            
            FragColor = vec4(color, 1.0);
        }
        """
        
        try:
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            self._cache_uniforms()
            print("Shaders compiled successfully")
        except Exception as e:
            print(f"Shader compilation failed: {e}")
            raise

    def _cache_uniforms(self):
        """Cache uniform locations for efficiency"""
        names = [
            'projection', 'view', 'model', 'point_count', 'scale_exponent',
            'max_iterations', 'point_size', 'color_mode', 'rotation_x', 'rotation_y'
        ]
        for name in names:
            self.uniforms[name] = glGetUniformLocation(self.shader_program, name)

    def create_vertex_buffer(self):
        """Create VBO with point indices"""
        indices = np.arange(self.point_count, dtype=np.float32)
        
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glBindVertexArray(0)
        self.vertex_count = len(indices)
        print(f"Created vertex buffer with {self.vertex_count} points")

    def init_gl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.create_shaders()
        self.create_vertex_buffer()
        print("OpenGL initialization complete")

    def get_projection_matrix(self):
        """Create projection matrix"""
        fov = 45.0
        aspect = self.width / self.height
        near, far = 0.1, 100.0
        
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        return np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)

    def get_view_matrix(self):
        """Create simple view matrix (just camera position, no rotation)"""
        return np.array([
            [1, 0, 0, -self.camera_pos[0]],
            [0, 1, 0, -self.camera_pos[1]],
            [0, 0, 1, -self.camera_pos[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def display(self):
        """Render frame"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_program)
        
        # Update uniforms
        proj = self.get_projection_matrix()
        view = self.get_view_matrix()
        model = np.eye(4, dtype=np.float32)  # Identity matrix
        
        glUniformMatrix4fv(self.uniforms['projection'], 1, GL_TRUE, proj)
        glUniformMatrix4fv(self.uniforms['view'], 1, GL_TRUE, view)
        glUniformMatrix4fv(self.uniforms['model'], 1, GL_TRUE, model)
        glUniform1f(self.uniforms['point_count'], float(self.point_count))
        glUniform1f(self.uniforms['scale_exponent'], float(self.scale_exponent))
        glUniform1i(self.uniforms['max_iterations'], self.max_iterations)
        glUniform1f(self.uniforms['point_size'], self.point_size)
        glUniform1i(self.uniforms['color_mode'], self.color_mode)
        glUniform1f(self.uniforms['rotation_x'], math.radians(self.rotation[0]))
        glUniform1f(self.uniforms['rotation_y'], math.radians(self.rotation[1]))
        
        # Draw points
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)
        
        pygame.display.flip()
        self._update_fps()

    def _update_fps(self):
        """Update FPS counter and window title"""
        self._frame_count += 1
        now = time.time()
        if now - self._last_fps_t >= 0.5:
            dt = now - self._last_fps_t
            self._fps = self._frame_count / dt
            self._frame_count = 0
            self._last_fps_t = now
            
            mode_names = ['Steps', 'Max Value', 'Convergence Speed']
            pygame.display.set_caption(
                f"Collatz Sphere - FPS: {self._fps:.1f} - "
                f"Color: {mode_names[self.color_mode]} - "
                f"Points: {self.point_count} - "
                f"Scale: 2^{self.scale_exponent:.1f}"
            )

    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            key = event.key
            
            if key == pygame.K_ESCAPE:
                return False
            elif key == pygame.K_c:
                self.color_mode = (self.color_mode + 1) % 3
                print(f"Color mode: {['Steps', 'Max Value', 'Convergence Speed'][self.color_mode]}")
            elif key == pygame.K_a:
                self.auto_rotate = not self.auto_rotate
                print(f"Auto-rotate: {'ON' if self.auto_rotate else 'OFF'}")
            elif key == pygame.K_r:
                self.camera_pos = [0.0, 0.0, 3.0]
                self.rotation = [0.0, 0.0]
                print("View reset")
            elif key == pygame.K_q:
                self.point_size = max(0.5, self.point_size - 0.5)
                print(f"Point size: {self.point_size}")
            elif key == pygame.K_e:
                self.point_size = min(10.0, self.point_size + 0.5)
                print(f"Point size: {self.point_size}")
            elif key == pygame.K_MINUS:
                self.scale_exponent = max(1.0, self.scale_exponent - 1.0)
                print(f"Scale exponent: {self.scale_exponent}")
            elif key == pygame.K_EQUALS:
                self.scale_exponent = min(40.0, self.scale_exponent + 1.0)
                print(f"Scale exponent: {self.scale_exponent}")
            elif key == pygame.K_o:
                old = self.point_count
                self.point_count = max(1000, self.point_count // 2)
                if self.point_count != old:
                    self.create_vertex_buffer()
            elif key == pygame.K_p:
                old = self.point_count
                self.point_count = min(500000, self.point_count * 2)
                if self.point_count != old:
                    self.create_vertex_buffer()
        
        return True

    def run(self):
        """Main loop"""
        self.initialize_pygame_and_opengl()
        self.init_gl()
        
        print("\nCollatz Sphere Viewer - Controls:")
        print("  Arrow keys / Mouse: Rotate view")
        print("  Scroll / PgUp/PgDn: Zoom")
        print("  C: Cycle color modes")
        print("  A: Toggle auto-rotation")
        print("  Q/E: Decrease/increase point size")
        print("  -/=: Adjust scale exponent")
        print("  O/P: Halve/double point count")
        print("  R: Reset view")
        print("  ESC: Quit")
        
        clock = pygame.time.Clock()
        running = True
        mouse_down = False
        last_mouse_pos = None
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_input(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_down = True
                        last_mouse_pos = pygame.mouse.get_pos()
                    elif event.button == 4:  # Scroll up
                        self.camera_pos[2] = max(0.5, self.camera_pos[2] - 0.2)
                    elif event.button == 5:  # Scroll down
                        self.camera_pos[2] = min(10.0, self.camera_pos[2] + 0.2)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                elif event.type == pygame.MOUSEMOTION and mouse_down:
                    current_pos = pygame.mouse.get_pos()
                    if last_mouse_pos:
                        dx = current_pos[0] - last_mouse_pos[0]
                        dy = current_pos[1] - last_mouse_pos[1]
                        self.rotation[1] += dx * 0.5
                        self.rotation[0] += dy * 0.5
                    last_mouse_pos = current_pos
            
            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if not mouse_down:
                if keys[pygame.K_LEFT]:
                    self.rotation[1] -= 2
                if keys[pygame.K_RIGHT]:
                    self.rotation[1] += 2
                if keys[pygame.K_UP]:
                    self.rotation[0] -= 2
                if keys[pygame.K_DOWN]:
                    self.rotation[0] += 2
                if keys[pygame.K_PAGEUP]:
                    self.camera_pos[2] = max(0.5, self.camera_pos[2] - 0.1)
                if keys[pygame.K_PAGEDOWN]:
                    self.camera_pos[2] = min(10.0, self.camera_pos[2] + 0.1)
            
            # Auto-rotation
            if self.auto_rotate:
                self.rotation[0] += self.rotate_speed[0]
                self.rotation[1] += self.rotate_speed[1]
            
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
        viewer = CollatzSphereViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Ensure pygame is installed: pip install pygame")
        print("3. Check graphics drivers are up to date")

if __name__ == "__main__":
    main()