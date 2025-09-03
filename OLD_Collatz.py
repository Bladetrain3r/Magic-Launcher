import math
import sys
import os
import json
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import multiprocessing
from multiprocessing import shared_memory, Manager, Lock
import traceback
import gc
import atexit
import signal
import time
import logging
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('collatz_sphere_renderer')

class FrameTracker:
    """Class to track progress of frame rendering across processes"""
    def __init__(self, total_frames, manager):
        self.completed = manager.Value('i', 0)
        self.failed = manager.Value('i', 0)
        self.total = total_frames
        self.lock = manager.Lock()
        self.last_report_time = time.time()
        self.report_interval = 2  # seconds
        
    def mark_complete(self):
        with self.lock:
            self.completed.value += 1
            self._report_progress()
    
    def mark_failed(self):
        with self.lock:
            self.failed.value += 1
            self._report_progress()
    
    def _report_progress(self):
        # Only report progress at intervals to reduce console spam
        current_time = time.time()
        if current_time - self.last_report_time >= self.report_interval:
            self.last_report_time = current_time
            progress = (self.completed.value / self.total) * 100
            logger.info(f"Progress: {self.completed.value}/{self.total} frames completed ({progress:.1f}%), {self.failed.value} failed")

class CollatzCalculator:
    """Class to perform Collatz calculations with caching"""
    def __init__(self, max_iterations=320):
        self.max_iterations = max_iterations
        self.cache = {}
    
    def is_power_of_two(self, n):
        """Check if a number is a power of two"""
        return n > 0 and (n & (n - 1)) == 0
    
    def calculate_stopping_time(self, n):
        """Calculate the Collatz stopping time with caching"""
        if n in self.cache:
            return self.cache[n]
            
        if n < 1:
            return None
            
        steps = 0
        current = n
        max_value = n
        power_two_steps = 0
        seen = set()
        first_power = None
        
        while not self.is_power_of_two(current) and steps < self.max_iterations and current not in seen:
            seen.add(current)
            if current & 1:  # Bitwise check for odd numbers (much faster than modulo)
                current = 3 * current + 1
                max_value = max(max_value, current)
            else:
                current //= 2
            steps += 1
        
        if self.is_power_of_two(current):
            first_power = current
            power_two_steps = int(math.log2(current))
        
        result = {
            'steps': steps,
            'power_steps': power_two_steps,
            'max_value': max_value,
            'converged': self.is_power_of_two(current),
            'first_power': first_power
        }
        
        self.cache[n] = result
        return result

class CollatzSphereRenderer:
    def __init__(self, config_path='collatz_sphere_config.json'):
        # Load configuration
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            self.config = {
                "width": 1280,
                "height": 1280,
                "max_iterations": 320,
                "resolution": 0.015,
                "framerate": 60,
                "duration": 6,
                "scale": 40.0,
                "batch_size": 120,
                "color": {
                    "max_power_norm": 64.0,
                    "max_value_norm": 32.0,
                    "value_weight": 0.6,
                    "z_weight": 0.5,
                    "step_weight": 1.0
                }
            }
        
        # Initialize visualization parameters
        self.width = self.config.get('width', 1280)
        self.height = self.config.get('height', 1280)
        self.scale = self.config.get('scale', 40.0)
        self.max_iterations = self.config.get('max_iterations', 320)
        self.resolution = self.config.get('resolution', 0.015)
        self.framerate = self.config.get('framerate', 60)
        self.duration = self.config.get('duration', 6)
        self.total_frames = self.framerate * self.duration
        
        # Color mapping parameters
        self.color_params = self.config.get('color', {
            'max_power_norm': 64.0,
            'max_value_norm': 32.0,
            'value_weight': 0.6,
            'z_weight': 0.5,
            'step_weight': 1.0
        })
        
        # Batch size for frame rendering
        self.batch_size = self.config.get('batch_size', 120)
        
        # Calculate optimal thread count
        mem_info = psutil.virtual_memory()
        mem_per_thread = 100 * 1024 * 1024  # 100MB per thread as a conservative estimate
        mem_based_threads = max(1, int(mem_info.available * 0.7 / mem_per_thread))
        cpu_based_threads = max(1, multiprocessing.cpu_count() - 1)  # Leave 1 core free
        self.thread_count = int(os.environ.get('RENDER_THREADS', min(mem_based_threads, cpu_based_threads)))
        logger.info(f"Using {self.thread_count} render threads (memory: {mem_info.available/1024/1024:.0f}MB available)")
        
        # Shared resources and manager
        self.shared_resources = []
        self.manager = Manager()
        
        # Setup exit handler
        atexit.register(self.cleanup_resources)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Initialize a Collatz calculator
        self.calculator = CollatzCalculator(max_iterations=self.max_iterations)
        
        # Generate sphere points and share them
        self.generate_sphere_points()
        
    def generate_sphere_points(self):
        """Pre-generate sphere points and share them via shared memory"""
        logger.info("Generating sphere points...")
        
        # Calculate total number of points
        theta_steps = int(2 * np.pi / self.resolution)
        phi_steps = int(np.pi / self.resolution)
        total_points = theta_steps * phi_steps
        
        # Create arrays to store points, values and visibility
        points = []
        collatz_values = []
        
        # Generate evenly spaced points on a sphere
        for i, theta in enumerate(np.linspace(0, 2*np.pi, theta_steps)):
            for j, phi in enumerate(np.linspace(0, np.pi, phi_steps)):
                x = math.sin(phi) * math.cos(theta)
                y = math.sin(phi) * math.sin(theta)
                z = math.cos(phi)
                
                # Map spherical coordinates to a number
                n = self._map_to_number(x, y, z)
                
                # Only add points that lead to convergence
                result = self.calculator.calculate_stopping_time(n)
                if result and result['converged']:
                    points.append([x, y, z])
                    
                    # Store relevant Collatz properties for each point
                    collatz_values.append([
                        result['steps'],
                        result['max_value'],
                        result['power_steps']
                    ])
                
                # Progress reporting
                point_index = i * phi_steps + j
                if point_index % 10000 == 0:
                    progress = (point_index / total_points) * 100
                    logger.info(f"Point generation: {point_index}/{total_points} ({progress:.1f}%)")
        
        logger.info(f"Generated {len(points)} valid points")
        
        # Convert to numpy arrays
        self.points = np.array(points, dtype=np.float32)
        self.collatz_values = np.array(collatz_values, dtype=np.float32)
        
        # Create shared memory for points
        self.points_shm = shared_memory.SharedMemory(create=True, size=self.points.nbytes)
        self.shared_resources.append(self.points_shm)
        shared_points = np.ndarray(self.points.shape, dtype=self.points.dtype, buffer=self.points_shm.buf)
        np.copyto(shared_points, self.points)
        
        # Create shared memory for Collatz values
        self.values_shm = shared_memory.SharedMemory(create=True, size=self.collatz_values.nbytes)
        self.shared_resources.append(self.values_shm)
        shared_values = np.ndarray(self.collatz_values.shape, dtype=self.collatz_values.dtype, buffer=self.values_shm.buf)
        np.copyto(shared_values, self.collatz_values)
                
    def _map_to_number(self, x, y, z):
        """Map 3D coordinates to a Collatz sequence number"""
        r = math.sqrt(x*x + y*y + z*z)
        
        # Base mapping with some variation
        base_number = int(r * math.pow(2, self.scale))
        
        # Apply pattern-based adjustments
        patterns = {
            '101': 1.1,    # L-type harbor pattern
            '111': 0.9,    # Mersenne-like pattern
            '1010': 1.05,  # Alternating pattern
        }
        
        for pattern, factor in patterns.items():
            if self._has_bit_pattern(base_number, pattern):
                base_number = int(base_number * factor)
        
        return max(1, base_number)
        
    def _has_bit_pattern(self, n, pattern):
        """Check if number contains specific binary pattern."""
        bin_str = bin(n)[2:]  # Convert to binary, remove '0b' prefix
        return pattern in bin_str
        
    def cleanup_resources(self):
        """Clean up any shared memory resources"""
        for shm in self.shared_resources:
            try:
                shm.close()
                shm.unlink()
                logger.info(f"Cleaned up shared memory resource: {shm.name}")
            except Exception as e:
                logger.error(f"Error cleaning up shared memory: {str(e)}")
        
        # Clear list after cleanup
        self.shared_resources = []

    def signal_handler(self, sig, frame):
        """Handle keyboard interrupts gracefully"""
        logger.info("\nInterrupted! Cleaning up resources...")
        self.cleanup_resources()
        sys.exit(0)
        
    @staticmethod
    def render_frame_static(frame_args):
        """Static method for multiprocessing to render a single frame"""
        try:
            # Unpack frame arguments
            (frame, points_shm_name, values_shm_name, point_count, values_count, output_dir,
             width, height, color_params, framerate, duration, tracker) = frame_args
             
            # Access shared memory for points
            points_shm = shared_memory.SharedMemory(name=points_shm_name)
            points = np.ndarray((point_count, 3), dtype=np.float32, buffer=points_shm.buf)
            
            # Access shared memory for Collatz values
            values_shm = shared_memory.SharedMemory(name=values_shm_name)
            collatz_values = np.ndarray((values_count, 3), dtype=np.float32, buffer=values_shm.buf)
            
            # Calculate camera rotation based on frame
            total_frames = framerate * duration
            rotation_angle = (frame / total_frames) * 360.0 * 2
            
            # Initialize pygame for this process
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            pygame.init()
            display = pygame.display.set_mode(
                (width, height), 
                pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN
            )
            
            # Setup OpenGL
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_POINT_SMOOTH)
            glPointSize(2.0)
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, (width / height), 0.1, 50.0)
            glMatrixMode(GL_MODELVIEW)
            
            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Position camera
            glTranslatef(0, 0, -2)

            # Flat rotation offset
            glRotatef(2, 0.0, 0.0, 0.0)
            
            # Apply rotation
            glRotatef(rotation_angle, 0.0, 0.5, 0.25)  # Rotation around an angled axis
            
            # Render points with their colors
            glBegin(GL_POINTS)
            for i in range(len(points)):
                # Get point coordinates
                point = points[i]
                
                # Get Collatz values for coloring
                steps = collatz_values[i][0]
                max_value = collatz_values[i][1]
                z_coord = point[2]
                
                # Calculate color (same as in original code)
                max_iterations = color_params.get('max_iterations', 320)
                max_value_norm = color_params.get('max_value_norm', 32.0)
                
                steps_norm = min(1.0, steps / max_iterations)
                value_norm = min(1.0, math.log2(max_value) / max_value_norm) if max_value > 0 else 0
                z_norm = (z_coord + 1) / 2
                
                # Frame-specific color adjustment (pulse effect)
                # frame_factor = 0.1 * math.sin(frame / 10.0) + 0.9
                frame_factor = 1.0
                
                color = (
                    steps_norm * frame_factor,
                    value_norm * 0.5 + z_norm * 0.5,
                    (1.0 - steps_norm) * z_norm * frame_factor
                )
                
                glColor3fv(color)
                glVertex3fv(point)
            glEnd()
            
            # Capture frame
            frame_data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
            surface = pygame.image.fromstring(frame_data, (width, height), 'RGB')
            
            # Flip the image vertically (OpenGL coordinates are bottom-left)
            surface = pygame.transform.flip(surface, False, True)
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save frame
            output_path = os.path.join(output_dir, f'frame_{frame:08d}.bmp')
            pygame.image.save(surface, output_path)
            
            # Mark frame as complete
            tracker.mark_complete()
            
            # Clean up resources
            points_shm.close()
            values_shm.close()
            pygame.quit()
            
            # Free memory
            del surface
            del frame_data
            gc.collect()
            
        except Exception as e:
            if tracker:
                tracker.mark_failed()
            logger.error(f"Error rendering frame {frame}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Make sure to close shared memory even on error
            try:
                points_shm.close()
                values_shm.close()
            except:
                pass
                
    def generate_animation_frames(self, output_dir='./collatz_frames'):
        """Generate animation frames in batches with progress tracking"""
        try:
            logger.info(f"Preparing to render {self.total_frames} frames using {self.thread_count} processes")

            # Clear output directory
            os.makedirs(output_dir, exist_ok=True)
            for f in os.listdir(output_dir):
                os.remove(os.path.join(output_dir, f))
            
            # Setup progress tracking
            tracker = FrameTracker(self.total_frames, self.manager)
            
            # Process frames in batches to manage memory better
            for batch_start in range(0, self.total_frames, self.batch_size):
                batch_end = min(batch_start + self.batch_size, self.total_frames)
                batch_size = batch_end - batch_start
                
                logger.info(f"Processing batch {batch_start//self.batch_size + 1} " 
                          f"(frames {batch_start}-{batch_end-1}, {batch_size} frames)")
                
                # Prepare frame rendering arguments for this batch
                frame_args = [
                    (frame, self.points_shm.name, self.values_shm.name, 
                     len(self.points), len(self.collatz_values),
                     output_dir, self.width, self.height, 
                     self.color_params, self.framerate, self.duration,
                     tracker) 
                    for frame in range(batch_start, batch_end)
                ]
                
                # Process this batch
                with multiprocessing.Pool(processes=self.thread_count) as pool:
                    pool.map(self.render_frame_static, frame_args)
                
                # Explicitly call garbage collection between batches
                gc.collect()
                
                # Check if we should take a short break between batches
                if batch_end < self.total_frames:
                    logger.info("Short pause between batches to manage memory...")
                    time.sleep(1)  # Short pause between batches
            
            # Verify all frames were created
            missing_frames = []
            for frame in range(self.total_frames):
                frame_path = os.path.join(output_dir, f'frame_{frame:08d}.bmp')
                if not os.path.exists(frame_path):
                    missing_frames.append(frame)
            
            if missing_frames:
                logger.warning(f"Missing {len(missing_frames)} frames. First few: {missing_frames[:5]}")
                
                # Re-render missing frames if there aren't too many
                if len(missing_frames) < self.total_frames * 0.1:  # Less than 10% missing
                    logger.info(f"Re-rendering {len(missing_frames)} missing frames...")
                    
                    # Prepare frame rendering arguments for missing frames
                    frame_args = [
                        (frame, self.points_shm.name, self.values_shm.name, 
                         len(self.points), len(self.collatz_values),
                         output_dir, self.width, self.height, 
                         self.color_params, self.framerate, self.duration,
                         tracker) 
                        for frame in missing_frames
                    ]
                    
                    # Process missing frames
                    with multiprocessing.Pool(processes=min(self.thread_count, len(missing_frames))) as pool:
                        pool.map(self.render_frame_static, frame_args)
            
            logger.info(f"Rendering complete. Frames saved to {os.path.abspath(output_dir)}")
            logger.info(f"Final stats: {tracker.completed.value} completed, {tracker.failed.value} failed")
            
        except Exception as e:
            logger.error(f"Error in animation generation: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            # Final cleanup
            self.cleanup_resources()

def create_default_config():
    """Create a default configuration file if it doesn't exist."""
    default_config = {
        "width": 1280,
        "height": 1280,
        "max_iterations": 320,
        "resolution": 0.015,
        "framerate": 60,
        "duration": 6,
        "scale": 40.0,
        "batch_size": 120,
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
        logger.info(f"Created default configuration file: {config_path}")

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Generate Collatz 3D sphere animation')
    parser.add_argument('--config', '-c', default='collatz_sphere_config.json', help='Path to config file')
    parser.add_argument('--output', '-o', default='./collatz_frames', help='Output directory for frames')
    parser.add_argument('--batch-size', '-b', type=int, help='Override batch size for frame processing')
    parser.add_argument('--threads', '-t', type=int, help='Override number of processing threads')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create default config if it doesn't exist
    create_default_config()
    
    # Create and run the renderer
    renderer = CollatzSphereRenderer(config_path=args.config)
    
    # Override batch size if specified
    if args.batch_size:
        renderer.batch_size = args.batch_size
        logger.info(f"Overriding batch size to {args.batch_size}")
    
    # Override thread count if specified
    if args.threads:
        renderer.thread_count = args.threads
        logger.info(f"Overriding thread count to {args.threads}")
    
    try:
        # Generate frames
        renderer.generate_animation_frames(output_dir=args.output)
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user. Cleaning up resources...")
        renderer.cleanup_resources()
        sys.exit(0)

if __name__ == "__main__":
    main()