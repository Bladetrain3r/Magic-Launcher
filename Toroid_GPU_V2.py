#!/usr/bin/env python3
"""
GPU4DToroidViewer (refactor)

4D toroidal point-cloud projected to 3D and rendered as GL_POINTS with GPU-side
param generation. Focused on correctness, clarity, and smooth interaction.

Key changes from the original:
- Fixed Fibonacci sampler (distinct incommensurate steps using φ powers)
- Removed destructive normalization that collapsed torus radii
- Cached uniform locations (no per-frame lookups)
- MSAA enabled; program-point-size enabled; consistent camera conventions
- View matrix order: rotate then translate (camera looks down -Z)
- Stable 4D→3D projection; optional alt projection factor
- Window caption shows FPS & current mode; toggles to up/downsample point count
- Small cleanup and error logging

Controls (additions):
  O / P          : halve / double point count (rebuilds VBO)
  MSAA           : on by default (4x)
Other controls remain from original and are listed on startup.
"""
from __future__ import annotations

import math
import os
import sys
import time
import ctypes
import platform as py_platform
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *  # noqa: F401 (not heavily used but kept for parity)
from OpenGL.GL import shaders


class GPU4DToroidViewer:
    def __init__(self):
        # Toroid parameters
        self.major_radius = 2.0
        self.minor_radius = 1.0
        self.point_count = 100_000
        self.distribution = 'grid'  # 'fibonacci', 'grid', 'random'

        # 4D rotation angles and position
        self.w_angle = 0.0
        self.w_position = 0.0
        self.xw_rotation_speed = 0.5
        self.yz_rotation_speed = 0.3
        self.zw_rotation_speed = 0.2
        self.auto_rotate_4d = False

        # 3D camera settings (camera looks toward -Z)
        self.camera_pos = [0.0, 0.0, 6.0]
        self.rotation = [0.0, 0.0, 0.0]  # degrees
        self.auto_rotate_3d = False
        self.auto_rotate_speed = [0.5, 0.5]  # deg per frame

        # Display settings
        self.width = 1920
        self.height = 1080
        self.point_size = 1.0
        self.base_point_size = 1.0
        self.color_mode = 0  # 0: w, 1: dist, 2: angle

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

    # ------------------ Pygame / GL init ------------------
    def _maybe_set_dpi_awareness(self):
        if py_platform.system() == 'Windows':
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def initialize_pygame_and_opengl(self):
        self._maybe_set_dpi_awareness()
        pygame.init()

        # GL attributes
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        # MSAA
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("GPU 4D Toroid Viewer (refactor)")

        # Force context creation and small wait
        pygame.display.flip()
        time.sleep(0.05)

        version = glGetString(GL_VERSION)
        if not version:
            raise RuntimeError("Failed to create a valid OpenGL context")
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version:   {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"Renderer:       {glGetString(GL_RENDERER).decode()}")

    def create_shaders(self):
        vertex_shader = r"""
        #version 330 core
        layout(location = 0) in float index;

        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        uniform float time_ms;
        uniform float point_count;
        uniform float major_radius;
        uniform float minor_radius;
        uniform int distribution_type; // 0=fib, 1=grid, 2=random
        uniform float w_angle;
        uniform float xw_speed;
        uniform float yz_speed;
        uniform float zw_speed;
        uniform float base_point_size;
        uniform float w_position;

        out vec3 FragPos;
        out vec4 ToroidCoord4D;
        out float WCoord;

        const float PHI = 1.61803398875; // golden ratio
        const float PI  = 3.14159265359;

        // Generate a 4D toroidal point from a single index using different distributions
        vec4 generate_toroid_point(float idx) {
            vec4 p;
            if (distribution_type == 0) {
                // Fibonacci lattice across angles using incommensurate steps
                float u1 = fract(idx / PHI);
                float u2 = fract(idx / (PHI*PHI));
                float u3 = fract(idx / (PHI*PHI*PHI));
                float u4 = fract(idx / (PHI*PHI*PHI*PHI));

                float th1 = 2.0*PI*u1;
                float th2 = 2.0*PI*u2;
                float th3 = 2.0*PI*u3;
                // th4 reserved if needed via u4

                float r1 = major_radius + minor_radius * cos(th3);
                p.x = r1 * cos(th1);
                p.y = r1 * sin(th1);

                float r2 = major_radius + minor_radius * sin(th3);
                p.z = r2 * cos(th2);
                p.w = r2 * sin(th2);
            } else if (distribution_type == 1) {
                // Grid (decompose index into 4 dims)
                float n = pow(point_count, 0.25);
                float i1 = mod(idx, n);
                float i2 = mod(floor(idx / n), n);
                float i3 = mod(floor(idx / (n*n)), n);
                float i4 = floor(idx / (n*n*n));

                float th1 = 2.0*PI * i1 / n;
                float th2 = 2.0*PI * i2 / n;
                float th3 = 2.0*PI * i3 / n;
                // float th4 = 2.0*PI * i4 / n; // not used yet

                float r1 = major_radius + minor_radius * cos(th3);
                p.x = r1 * cos(th1);
                p.y = r1 * sin(th1);

                float r2 = major_radius + minor_radius * sin(th3);
                p.z = r2 * cos(th2);
                p.w = r2 * sin(th2);
            } else {
                // Pseudo-random from index (deterministic)
                float th1 = fract(sin(idx * 12.9898) * 43758.5453) * 2.0 * PI;
                float th2 = fract(sin(idx * 78.233)  * 43758.5453) * 2.0 * PI;
                float th3 = fract(sin(idx * 45.164)  * 43758.5453) * 2.0 * PI;

                float r1 = major_radius + minor_radius * cos(th3);
                p.x = r1 * cos(th1);
                p.y = r1 * sin(th1);

                float r2 = major_radius + minor_radius * sin(th3);
                p.z = r2 * cos(th2);
                p.w = r2 * sin(th2);
            }
            return p;
        }

        vec3 project_4d_to_3d(vec4 p) {
            // Aggregate angle (manual control + optional time)
            float total = w_angle + (time_ms > 0.0 ? time_ms * 0.001 : 0.0);

            // XW rotation
            float cxw = cos(total * xw_speed);
            float sxw = sin(total * xw_speed);
            float nx = p.x * cxw - p.w * sxw;
            float nw = p.x * sxw + p.w * cxw;
            p.x = nx; p.w = nw;

            // YZ rotation
            float cyz = cos(total * yz_speed * 0.5);
            float syz = sin(total * yz_speed * 0.5);
            float ny = p.y * cyz - p.z * syz;
            float nz = p.y * syz + p.z * cyz;
            p.y = ny; p.z = nz;

            // ZW rotation
            float czw = cos(total * zw_speed * 0.3);
            float szw = sin(total * zw_speed * 0.3);
            nz = p.z * czw - p.w * szw;
            nw = p.z * szw + p.w * czw;
            p.z = nz; p.w = nw;

            // Translate along W after rotations
            p.w += w_position;
            WCoord = p.w;

            // 4D→3D perspective from W (stable)
            float denom = max(0.1, 1.0 + 0.5 * p.w);
            float k = 1.0 / denom;
            return p.xyz * k;
        }

        void main() {
            vec4 p4 = generate_toroid_point(index);
            ToroidCoord4D = p4;
            vec3 pos = project_4d_to_3d(p4);
            FragPos = pos;

            gl_Position = projection * view * model * vec4(pos, 1.0);
            gl_PointSize = base_point_size + base_point_size * (WCoord + 1.0) * 0.5;
        }
        """

        fragment_shader = r"""
        #version 330 core
        in vec3 FragPos;
        in vec4 ToroidCoord4D;
        in float WCoord;

        uniform int color_mode; // 0: W, 1: dist, 2: angle

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
            vec3 color;
            if (color_mode == 0) {
                float hue = (WCoord + 1.0) * 180.0;
                color = hsv_to_rgb(vec3(hue, 0.8, 0.9));
            } else if (color_mode == 1) {
                float dist = length(ToroidCoord4D);
                float hue = mod(dist * 120.0, 360.0);
                color = hsv_to_rgb(vec3(hue, 0.7, 0.8 + 0.2 * sin(dist * 5.0)));
            } else {
                float a1 = atan(ToroidCoord4D.y, ToroidCoord4D.x) + 3.14159;
                float a2 = atan(ToroidCoord4D.w, ToroidCoord4D.z) + 3.14159;
                float hue = (a1 + a2) * 57.2958;
                color = hsv_to_rgb(vec3(hue, 0.9, 0.8 + 0.2 * (WCoord + 1.0) * 0.5));
            }

            // soft depth tint (not linearized)
            float depth = gl_FragCoord.z;
            color *= (1.3 - depth * 0.3);
            FragColor = vec4(color, 1.0);
        }
        """

        try:
            vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
            self.shader_program = shaders.compileProgram(vs, fs)
            # Cache uniform locations once
            self._cache_uniforms()
            print("Shaders compiled & linked successfully.")
        except Exception as e:
            # Try to pull program log if available
            try:
                log = glGetProgramInfoLog(self.shader_program)
                if log:
                    print("Program log:", log.decode(errors='ignore'))
            except Exception:
                pass
            raise

    def _cache_uniforms(self):
        names = [
            'projection','view','model','time_ms','point_count','major_radius','minor_radius',
            'distribution_type','w_angle','xw_speed','yz_speed','zw_speed','color_mode',
            'w_position','base_point_size'
        ]
        for n in names:
            self.uniforms[n] = glGetUniformLocation(self.shader_program, n)

    def create_vertex_buffer(self):
        # Generate indices as float attribute
        indices = np.arange(self.point_count, dtype=np.float32)

        # Gen VAO/VBO
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
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.create_shaders()
        self.create_vertex_buffer()
        print("GPU initialization complete")

    # ------------------ Matrices ------------------
    def get_projection_matrix(self):
        fov = 45.0
        aspect = self.width / self.height
        near, far = 0.1, 100.0
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        m = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        return m

    def get_view_matrix(self):
        # Rotation matrices (degrees→radians)
        rx, ry, rz = [math.radians(a) for a in self.rotation]
        rot_x = np.eye(4, dtype=np.float32)
        rot_y = np.eye(4, dtype=np.float32)
        rot_z = np.eye(4, dtype=np.float32)
        # X
        rot_x[1,1] = math.cos(rx); rot_x[1,2] = -math.sin(rx)
        rot_x[2,1] = math.sin(rx); rot_x[2,2] =  math.cos(rx)
        # Y
        rot_y[0,0] =  math.cos(ry); rot_y[0,2] = math.sin(ry)
        rot_y[2,0] = -math.sin(ry); rot_y[2,2] = math.cos(ry)
        # Z
        rot_z[0,0] = math.cos(rz); rot_z[0,1] = -math.sin(rz)
        rot_z[1,0] = math.sin(rz); rot_z[1,1] =  math.cos(rz)

        translation = np.eye(4, dtype=np.float32)
        translation[0,3] = -self.camera_pos[0]
        translation[1,3] = -self.camera_pos[1]
        translation[2,3] = -self.camera_pos[2]

        # Rotate then translate
        view = rot_z @ rot_y @ rot_x @ translation
        return view

    # ------------------ Render ------------------
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_program)

        # Time for auto 4D rotation
        time_ms = float(pygame.time.get_ticks()) if self.auto_rotate_4d else 0.0

        # Upload matrices (numpy is row-major; pass transpose=GL_TRUE)
        proj = self.get_projection_matrix()
        view = self.get_view_matrix()
        model = np.eye(4, dtype=np.float32)
        glUniformMatrix4fv(self.uniforms['projection'], 1, GL_TRUE, proj)
        glUniformMatrix4fv(self.uniforms['view'],       1, GL_TRUE, view)
        glUniformMatrix4fv(self.uniforms['model'],      1, GL_TRUE, model)

        # Upload uniforms (many are static unless tweaked)
        glUniform1f(self.uniforms['time_ms'], time_ms)
        glUniform1f(self.uniforms['point_count'], float(self.point_count))
        glUniform1f(self.uniforms['major_radius'], float(self.major_radius))
        glUniform1f(self.uniforms['minor_radius'], float(self.minor_radius))

        dist_map = {'fibonacci': 0, 'grid': 1, 'random': 2}
        glUniform1i(self.uniforms['distribution_type'], dist_map.get(self.distribution, 1))

        glUniform1f(self.uniforms['w_angle'], float(self.w_angle))
        glUniform1f(self.uniforms['xw_speed'], float(self.xw_rotation_speed))
        glUniform1f(self.uniforms['yz_speed'], float(self.yz_rotation_speed))
        glUniform1f(self.uniforms['zw_speed'], float(self.zw_rotation_speed))
        glUniform1i(self.uniforms['color_mode'], int(self.color_mode))
        glUniform1f(self.uniforms['w_position'], float(self.w_position))
        glUniform1f(self.uniforms['base_point_size'], float(self.base_point_size))

        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)

        pygame.display.flip()
        self._tick_fps()

    # ------------------ FPS & Caption ------------------
    def _tick_fps(self):
        self._frame_count += 1
        now = time.time()
        if now - self._last_fps_t >= 0.5:
            dt = now - self._last_fps_t
            self._fps = self._frame_count / dt
            self._frame_count = 0
            self._last_fps_t = now
            pygame.display.set_caption(
                f"GPU 4D Toroid Viewer — FPS:{self._fps:5.1f} — {self.distribution} — color {self.color_mode} — points {self.vertex_count}"
            )

    # ------------------ Main loop ------------------
    def run(self):
        self.initialize_pygame_and_opengl()
        self.init_gl()
        self._print_controls()

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_keydown(event.key)

            # Continuous rotations / motions
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

        self._cleanup()
        pygame.quit()

    # ------------------ Input handling ------------------
    def _handle_keydown(self, key: int) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        elif key == pygame.K_r:
            self.camera_pos = [0.0, 0.0, 6.0]
            self.rotation = [0.0, 0.0, 0.0]
            self.w_angle = 0.0
            self.w_position = 0.0
            self.base_point_size = self.point_size = 2.0
            print("View reset")
        elif key in (pygame.K_PAGEUP, pygame.K_KP_PLUS):
            # Move forward (toward -Z)
            self.camera_pos[2] = max(0.5, self.camera_pos[2] - 0.5)
        elif key in (pygame.K_PAGEDOWN, pygame.K_KP_MINUS):
            # Move backward (toward +Z)
            self.camera_pos[2] += 0.5
        elif key == pygame.K_q:
            self.base_point_size = max(0.5, self.base_point_size - 0.5)
            print(f"Point size: {self.base_point_size:.1f}")
        elif key == pygame.K_e:
            self.base_point_size = min(10.0, self.base_point_size + 0.5)
            print(f"Point size: {self.base_point_size:.1f}")
        elif key == pygame.K_a:
            self.auto_rotate_3d = not self.auto_rotate_3d
            print(f"3D Auto-rotation: {'ON' if self.auto_rotate_3d else 'OFF'}")
        elif key == pygame.K_d:
            self.auto_rotate_4d = not self.auto_rotate_4d
            print(f"4D Auto-rotation: {'ON' if self.auto_rotate_4d else 'OFF'}")
        elif key == pygame.K_c:
            self.color_mode = (self.color_mode + 1) % 3
            print(f"Color mode: {['W','Distance','Angle'][self.color_mode]}")
        elif key == pygame.K_f:
            distributions = ['fibonacci', 'grid', 'random']
            i = distributions.index(self.distribution)
            self.distribution = distributions[(i + 1) % 3]
            print(f"Distribution: {self.distribution}")
        elif key in (pygame.K_EQUALS, pygame.K_PLUS):
            self.major_radius = min(5.0, self.major_radius + 0.1)
            print(f"Major radius: {self.major_radius:.1f}")
        elif key == pygame.K_MINUS:
            self.major_radius = max(0.5, self.major_radius - 0.1)
            print(f"Major radius: {self.major_radius:.1f}")
        elif key == pygame.K_RIGHTBRACKET:
            self.minor_radius = min(3.0, self.minor_radius + 0.1)
            print(f"Minor radius: {self.minor_radius:.1f}")
        elif key == pygame.K_LEFTBRACKET:
            self.minor_radius = max(0.1, self.minor_radius - 0.1)
            print(f"Minor radius: {self.minor_radius:.1f}")
        elif key == pygame.K_1:
            self.xw_rotation_speed *= 1.2
            print(f"XW rotation speed: {self.xw_rotation_speed:.2f}")
        elif key == pygame.K_2:
            self.yz_rotation_speed *= 1.2
            print(f"YZ rotation speed: {self.yz_rotation_speed:.2f}")
        elif key == pygame.K_3:
            self.zw_rotation_speed *= 1.2
            print(f"ZW rotation speed: {self.zw_rotation_speed:.2f}")
        elif key == pygame.K_o:
            # halve point count (min 1k)
            old = self.point_count
            self.point_count = max(1_000, self.point_count // 2)
            if self.point_count != old:
                self.create_vertex_buffer()
        elif key == pygame.K_p:
            # double point count (cap 1M)
            old = self.point_count
            self.point_count = min(1_000_000, self.point_count * 2)
            if self.point_count != old:
                self.create_vertex_buffer()
        return True

    # ------------------ Misc ------------------
    def _print_controls(self):
        print("\nGPU 4D Toroid Viewer (refactor)")
        print("\nControls:")
        print("  Arrow keys: Rotate 3D view")
        print("  Page Up/Down or Numpad +/-: Zoom in/out")
        print("  W/S: Rotate in 4D (W dimension)")
        print("  T/G: Pan along W axis (4th dimension)")
        print("  Q/E: Decrease/Increase point size")
        print("  A: Toggle 3D auto-rotation")
        print("  D: Toggle 4D auto-rotation")
        print("  C: Cycle color modes")
        print("  F: Cycle distribution (fibonacci/grid/random)")
        print("  +/-: Adjust major radius  |  [/]: Adjust minor radius")
        print("  1/2/3: Increase XW / YZ / ZW rotation speeds")
        print("  O / P: Halve / Double point count (rebuild VBO)")
        print("  R: Reset view")
        print("  ESC: Quit")

    def _cleanup(self):
        try:
            if self.vao:
                glDeleteVertexArrays(1, [self.vao])
            if self.vbo:
                glDeleteBuffers(1, [self.vbo])
            if self.shader_program:
                glDeleteProgram(self.shader_program)
        except Exception:
            pass


def main():
    try:
        viewer = GPU4DToroidViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PyOpenGL is installed: pip install PyOpenGL PyOpenGL_accelerate")
        print("2. Ensure pygame is installed: pip install pygame")
        print("3. Check your graphics drivers are up to date")
        print("4. Try reducing point_count if performance is poor")


if __name__ == "__main__":
    main()
