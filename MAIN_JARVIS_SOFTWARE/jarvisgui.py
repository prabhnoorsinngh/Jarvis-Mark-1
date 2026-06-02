"""
JARVIS MARK-I - ULTIMATE CINEMATIC DESKTOP OVERLAY
Tony Stark-Level AI Interface with Full Iron Man HUD Experience
Created by Singh Industries | Engineered by: Mr. Prabhnoor Singh
"""

import sys
import os
import json
import logging
import random
import math
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import psutil
import pygame
import numpy as np

from jarvis import YOUTUBE_DL_AVAILABLE, JarvisMarkIEnhanced

# ============================================================================
# SETUP PROFESSIONAL LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_ultimate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('JARVIS_ULTIMATE')

# Initialize pygame mixer for cinematic sound
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    pygame.mixer.set_num_channels(16)
    SOUND_ENABLED = True
except:
    SOUND_ENABLED = False
    logger.warning("Sound system not available")

# ============================================================================
# PROFESSIONAL SPLASH SCREEN
# ============================================================================
class StarkSplashScreen(QWidget):
    """Tony Stark-Level Professional Splash Screen"""
    
    finished = pyqtSignal()
    
    def __init__(self, sound_system):
        super().__init__()
        self.sound = sound_system
        self.start_time = time.time()
        
        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set size to 800x500 for a professional look
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            (screen.width() - 800) // 2,
            (screen.height() - 500) // 2,
            800, 500
        )
        
        # Animation variables
        self.phase = 0
        self.progress = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.scan_y = 0
        self.reactor_glow = 0
        self.boot_complete = False
        
        # Boot sequence messages
        self.boot_texts = [
            "INITIALIZING NEURAL NETWORK",
            "LOADING AI MODULES",
            "CALIBRATING VOICE MATRIX",
            "SYNCHRONIZING SYSTEMS",
            "ACTIVATING HUD INTERFACE",
            "READY FOR DEPLOYMENT"
        ]
        self.current_text = ""
        self.text_index = 0
        self.char_index = 0
        
        # Create reactor data
        self.reactor_data = self.generate_reactor_data()
        
        # Start animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(30)  # ~33 FPS
        
        # Play boot sound
        if SOUND_ENABLED:
            self.sound.play_sound("boot")
        
        logger.info("Professional splash screen initialized")
    
    def generate_reactor_data(self):
        """Generate arc reactor data"""
        data = []
        rings = 3
        segments = 12
        
        for ring in range(rings):
            radius = 40 + ring * 25
            for seg in range(segments):
                angle = (seg / segments) * 2 * math.pi
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                
                data.append({
                    'x': x, 'y': y, 'ring': ring,
                    'angle': angle,
                    'size': 2 + ring,
                    'alpha': 200 - ring * 50,
                    'phase': random.uniform(0, 6.28)
                })
        
        return data
    
    def update_animation(self):
        """Update splash screen animation"""
        current_time = time.time() - self.start_time
        
        # Phase 0: Black screen (0.5s)
        if self.phase == 0:
            if current_time > 0.5:
                self.phase = 1
                self.start_time = time.time()
                if SOUND_ENABLED:
                    self.sound.play_sound("arc_reactor")
        
        # Phase 1: Reactor ignites (1.5s)
        elif self.phase == 1:
            phase_time = current_time
            self.reactor_glow = min(1.0, phase_time * 2)
            if phase_time > 1.5:
                self.phase = 2
                self.start_time = time.time()
        
        # Phase 2: Text appears with typewriter effect (3s)
        elif self.phase == 2:
            phase_time = current_time
            
            # Typewriter effect
            if phase_time > self.text_index * 0.5:
                if self.text_index < len(self.boot_texts):
                    if self.char_index < len(self.boot_texts[self.text_index]):
                        self.current_text = self.boot_texts[self.text_index][:self.char_index + 1]
                        self.char_index += 1
                    else:
                        self.text_index += 1
                        self.char_index = 0
            
            # Update scan line
            self.scan_y = (self.scan_y + 6) % self.height()
            
            if phase_time > 3.0:
                self.phase = 3
                self.boot_complete = True
                self.start_time = time.time()
        
        # Phase 3: Complete and ready (1s)
        elif self.phase == 3:
            phase_time = current_time
            
            # Pulse effect
            self.pulse += 0.03 * self.pulse_dir
            if self.pulse >= 1.0 or self.pulse <= 0.0:
                self.pulse_dir *= -1
            
            if phase_time > 1.0:
                self.finish()
        
        self.update()
    
    def finish(self):
        """Finish splash screen"""
        self.animation_timer.stop()
        self.finished.emit()
        self.close()
    
    def paintEvent(self, event):
        """Paint the splash screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Fill background
        if self.phase == 0:
            painter.fillRect(self.rect(), Qt.black)
            return
        
        # Draw dark blue gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(5, 10, 25))
        gradient.setColorAt(1, QColor(10, 20, 40))
        painter.fillRect(self.rect(), gradient)
        
        center_x, center_y = self.width() // 2, self.height() // 2
        
        # Draw subtle grid
        painter.setPen(QPen(QColor(0, 100, 200, 30), 1))
        grid_size = 40
        
        # Horizontal lines
        for i in range(0, self.height(), grid_size):
            painter.drawLine(0, i, self.width(), i)
        
        # Vertical lines
        for i in range(0, self.width(), grid_size):
            painter.drawLine(i, 0, i, self.height())
        
        # Draw arc reactor
        if self.phase >= 1:
            self.draw_arc_reactor(painter, center_x, center_y - 50)
        
        # Draw scan line
        if self.phase >= 2:
            painter.setPen(QPen(QColor(0, 255, 255, 100), 3))
            painter.drawLine(0, int(self.scan_y), self.width(), int(self.scan_y))
            
            # Scan glow
            painter.setPen(Qt.NoPen)
            scan_gradient = QLinearGradient(0, self.scan_y - 10, 0, self.scan_y + 10)
            scan_gradient.setColorAt(0, QColor(0, 255, 255, 0))
            scan_gradient.setColorAt(0.5, QColor(0, 255, 255, 50))
            scan_gradient.setColorAt(1, QColor(0, 255, 255, 0))
            painter.setBrush(QBrush(scan_gradient))
            painter.drawRect(0, int(self.scan_y - 10), self.width(), 20)
        
        # Draw boot text
        if self.phase >= 2 and self.current_text:
            # Text background
            text_rect = QRect(center_x - 300, center_y + 50, 600, 40)
            painter.setPen(QPen(QColor(0, 100, 200, 100), 2))
            painter.setBrush(QColor(0, 30, 60, 150))
            painter.drawRoundedRect(text_rect, 5, 5)
            
            # Text
            painter.setPen(QColor(0, 255, 255))
            painter.setFont(QFont("Consolas", 14, QFont.Bold))
            painter.drawText(text_rect, Qt.AlignCenter, self.current_text)
            
            # Cursor blink
            if time.time() % 1 < 0.5:
                cursor_width = painter.fontMetrics().width(self.current_text)
                painter.fillRect(center_x + cursor_width//2, center_y + 70, 8, 3, QColor(0, 255, 255))
        
        # Draw JARVIS title
        if self.phase >= 2:
            # Title with glow effect
            for i in range(3, 0, -1):
                glow_alpha = 100 // i
                painter.setPen(QPen(QColor(0, 200, 255, glow_alpha), i))
                painter.setFont(QFont("Arial", 32 + i * 2, QFont.Bold))
                painter.drawText(QRect(0, 80, self.width(), 60), 
                               Qt.AlignCenter, "J.A.R.V.I.S")
            
            # Main title
            painter.setPen(QColor(0, 255, 255))
            painter.setFont(QFont("Arial", 32, QFont.Bold))
            painter.drawText(QRect(0, 80, self.width(), 60), 
                           Qt.AlignCenter, "J.A.R.V.I.S")
            
            # Subtitle
            painter.setPen(QColor(150, 220, 255))
            painter.setFont(QFont("Arial", 16))
            painter.drawText(QRect(0, 140, self.width(), 40), 
                           Qt.AlignCenter, "MARK I - ULTIMATE EDITION")
        
        # Draw status
        if self.boot_complete:
            status_color = QColor(0, 255, 100) if self.pulse > 0.5 else QColor(0, 200, 80)
            painter.setPen(status_color)
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(QRect(0, self.height() - 60, self.width(), 40), 
                           Qt.AlignCenter, "SYSTEM READY - CLICK TO CONTINUE")
            
            # Pulse dot
            pulse_size = 6 + 4 * self.pulse
            painter.setBrush(status_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_x - int(pulse_size//2), self.height() - 75, 
                              int(pulse_size), int(pulse_size))
        
        # Draw copyright
        painter.setPen(QColor(100, 150, 200, 150))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(QRect(0, self.height() - 30, self.width(), 30),
                       Qt.AlignCenter, "© 2024 Singh Industries | Engineered by: Mr. Prabhnoor Singh")
    
    def draw_arc_reactor(self, painter, center_x, center_y):
        """Draw arc reactor - FIXED VERSION"""
        current_time = time.time()
        
        # Multiple glow layers
        for layer in range(3):
            glow_size = int(150 * self.reactor_glow * (1 - layer * 0.3))
            if glow_size <= 0:
                continue
                
            gradient = QRadialGradient(center_x, center_y, glow_size)
            
            alpha = 150 - layer * 50
            layer_color = QColor(0, 200, 255, alpha)
            
            if layer == 0:
                gradient.setColorAt(0, layer_color.lighter(150))
                gradient.setColorAt(0.3, layer_color)
                gradient.setColorAt(1, Qt.transparent)
            else:
                gradient.setColorAt(0, layer_color)
                gradient.setColorAt(1, Qt.transparent)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_x - glow_size, center_y - glow_size,
                              glow_size * 2, glow_size * 2)
        
        # Multiple rotating rings
        for ring in range(3):
            radius = 40 + ring * 25
            segments = 8 + ring * 2
            rotation = current_time * (20 + ring * 15) * (1 if ring % 2 == 0 else -1)
            thickness = 2 + ring
            
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(rotation)
            
            for seg in range(segments):
                if seg % 2 == 0:
                    painter.save()
                    angle = (360 / segments) * seg
                    painter.rotate(angle)
                    
                    # Animated segment
                    segment_length = 15 + ring * 5
                    for glow in range(2):
                        glow_alpha = 200 - glow * 80
                        glow_thickness = thickness + glow
                        pen = QPen(QColor(0, 200, 255, glow_alpha), glow_thickness)
                        pen.setCapStyle(Qt.RoundCap)
                        painter.setPen(pen)
                        
                        offset = glow * 1
                        painter.drawLine(radius - segment_length//2 + offset, 0,
                                       radius + segment_length//2 - offset, 0)
                    
                    painter.restore()
            
            painter.restore()
        
        # Central core
        core_size = int(30 * (0.7 + self.pulse * 0.6))
        
        if core_size > 0:
            core_gradient = QRadialGradient(center_x, center_y, core_size)
            core_gradient.setColorAt(0, QColor(255, 255, 255, 255))
            core_gradient.setColorAt(0.2, QColor(0, 200, 255, 220))
            core_gradient.setColorAt(0.5, QColor(0, 150, 255, 180))
            core_gradient.setColorAt(1, Qt.transparent)
            
            painter.setBrush(QBrush(core_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_x - core_size, center_y - core_size,
                              core_size * 2, core_size * 2)
    
    def mousePressEvent(self, event):
        """Click to continue"""
        if self.boot_complete:
            self.finish()

# ============================================================================
# IRON MAN THEME SOUNDS (SIMPLIFIED)
# ============================================================================
class IronManSoundSystem:
    """Professional Iron Man-themed sound system"""
    
    def __init__(self):
        self.sounds = {}
        if SOUND_ENABLED:
            self.load_iron_man_sounds()
        logger.info("Iron Man Sound System initialized")
    
    def load_iron_man_sounds(self):
        """Load Iron Man cinematic sounds"""
        sound_presets = {
            "boot": self.generate_boot_sound(),
            "arc_reactor": self.generate_arc_reactor_sound(),
            "hud_activate": self.generate_hud_sound(),
            "success": self.generate_success_sound(),
            "error": self.generate_error_sound()
        }
        
        # Convert numpy arrays to pygame sounds
        for name, data in sound_presets.items():
            if data is not None:
                try:
                    sound = pygame.sndarray.make_sound(data)
                    self.sounds[name] = sound
                except:
                    pass
    
    def generate_boot_sound(self):
        """Generate Iron Man boot sequence sound"""
        duration = 2.0
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Multiple frequencies for epic boot
        freq1 = 220 * np.exp(-t) * np.sin(2 * np.pi * 55 * t)
        freq2 = 440 * np.exp(-t/2) * np.sin(2 * np.pi * 110 * t)
        
        sound = 0.5 * (freq1 + 0.7 * freq2)
        sound = np.int16(sound * 32767)
        return np.vstack((sound, sound)).T
    
    def generate_arc_reactor_sound(self):
        """Generate arc reactor humming sound"""
        duration = 3.0
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Complex reactor hum
        base = 120 * np.sin(2 * np.pi * 60 * t)
        harmonic1 = 60 * np.sin(2 * np.pi * 180 * t + 0.5)
        pulse = 40 * np.exp(-np.mod(t, 0.5) * 10) * np.sin(2 * np.pi * 240 * t)
        
        sound = 0.3 * (base + harmonic1 + pulse)
        sound = np.int16(sound * 32767)
        return np.vstack((sound, sound)).T
    
    def generate_hud_sound(self):
        """Generate HUD activation sound"""
        duration = 0.5
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Quick ascending sweep
        sweep = np.linspace(2000, 6000, len(t))
        sound = 0.7 * np.sin(2 * np.pi * sweep * t) * np.exp(-t * 3)
        
        sound = np.int16(sound * 32767)
        return np.vstack((sound, sound)).T
    
    def generate_success_sound(self):
        """Generate success sound"""
        duration = 0.8
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Ascending success tone
        sweep = np.linspace(800, 1200, len(t))
        sound = 0.6 * np.sin(2 * np.pi * sweep * t) * np.exp(-t * 2)
        
        sound = np.int16(sound * 32767)
        return np.vstack((sound, sound)).T
    
    def generate_error_sound(self):
        """Generate error sound"""
        duration = 0.8
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Descending error tone
        sweep = np.linspace(1200, 400, len(t))
        sound = 0.7 * np.sin(2 * np.pi * sweep * t) * np.exp(-t * 3)
        
        sound = np.int16(sound * 32767)
        return np.vstack((sound, sound)).T
    
    def play_sound(self, name, volume=0.7):
        """Play a sound effect"""
        if not SOUND_ENABLED or name not in self.sounds:
            return
            
        try:
            channel = pygame.mixer.find_channel()
            if channel:
                self.sounds[name].set_volume(volume)
                channel.play(self.sounds[name])
                logger.info(f"Playing sound: {name}")
        except Exception as e:
            logger.error(f"Sound play error: {e}")

# ============================================================================
# FIXED BACKEND INTEGRATOR WITH PROPER STATE MANAGEMENT
# ============================================================================
class JarvisBackendIntegrator(QThread):
    """Fixed backend integration with robust state management"""
    
    # Define signals
    state_changed = pyqtSignal(str)
    command_received = pyqtSignal(str)
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    hotword_detected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.jarvis_instance = None
        self.running = True
        self.voice_active = True
        self.auto_listen = True
        self.command_queue = queue.Queue()
        self.current_state = "ONLINE"
        self.last_command_time = 0
        self.listen_interval = 2.0
        self.last_auto_listen = time.time()
        self.state_lock = threading.Lock()  # Add lock for state safety
        self.active_listening = False  # Track if actively listening
        self.force_return_timer = None  # Timer to force return to ONLINE
        
        logger.info("Fixed Backend Integrator initialized")
    
    def connect_to_jarvis(self, jarvis_instance):
        """Connect to existing JARVIS instance from main logic"""
        self.jarvis_instance = jarvis_instance
        logger.info("✅ JARVIS instance connected to backend")
        self.set_state("ONLINE")
    
    def set_state(self, new_state):
        """Thread-safe state setting"""
        with self.state_lock:
            if self.current_state != new_state:
                logger.info(f"State change: {self.current_state} -> {new_state}")
                self.current_state = new_state
                self.state_changed.emit(new_state)
                
                # Cancel any force return timer when state changes
                if self.force_return_timer:
                    self.force_return_timer.cancel()
                    self.force_return_timer = None
                
                # Set force return timer for LISTENING state
                if new_state == "LISTENING":
                    self.force_return_timer = threading.Timer(8.0, self.force_return_to_online)
                    self.force_return_timer.daemon = True
                    self.force_return_timer.start()
    
    def force_return_to_online(self):
        """Force return to ONLINE state if stuck"""
        with self.state_lock:
            if self.current_state in ["LISTENING", "PROCESSING", "SPEAKING"]:
                logger.warning(f"Force returning from {self.current_state} to ONLINE")
                self.current_state = "ONLINE"
                self.state_changed.emit("ONLINE")
                self.active_listening = False
    
    def safe_listen(self, timeout=4):
        """Safe listening with timeout and cleanup"""
        if not self.jarvis_instance or not hasattr(self.jarvis_instance, 'listen'):
            return None
        
        try:
            self.active_listening = True
            # Use shorter timeout for faster recovery
            command = self.jarvis_instance.listen(timeout=min(timeout, 4))
            self.active_listening = False
            return command
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self.active_listening = False
            return None
        finally:
            # Ensure listening flag is always cleared
            self.active_listening = False
    
    def safe_hotword_check(self):
        """Safe hotword check with timeout"""
        if not self.jarvis_instance or not hasattr(self.jarvis_instance, 'hotword_listen'):
            return False
        
        try:
            # Quick timeout for hotword check
            return self.jarvis_instance.hotword_listen()
        except Exception as e:
            logger.error(f"Hotword check error: {e}")
            return False
    
    def run(self):
        """Main backend thread with safe state management"""
        logger.info("Starting backend thread")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Skip processing if not connected
                if not self.jarvis_instance:
                    time.sleep(0.5)
                    continue
                
                # Process queued commands first (they have priority)
                self.process_queued_commands_safe()
                
                # Check current state
                current_state = self.current_state
                
                if current_state == "ONLINE":
                    # ONLINE state - check for hotword or auto-listen
                    if self.voice_active and current_time - self.last_command_time > 1.0:
                        # Auto-listen if enabled
                        if self.auto_listen and current_time - self.last_auto_listen >= self.listen_interval:
                            self.last_auto_listen = current_time
                            self.attempt_auto_listen()
                        
                        # Hotword check
                        if self.safe_hotword_check():
                            logger.info("Hotword detected!")
                            self.hotword_detected.emit()
                            self.set_state("LISTENING")
                            
                            # Listen for command
                            command = self.safe_listen(timeout=5)
                            if command and len(command.strip()) > 2:
                                self.command_received.emit(command)
                                self.process_command_safe(command)
                            else:
                                self.set_state("ONLINE")
                
                elif current_state == "LISTENING":
                    # LISTENING state - should only be here briefly
                    # If stuck, force return after timeout
                    if current_time - self.last_command_time > 6.0:
                        logger.warning("LISTENING state timeout, forcing return")
                        self.set_state("ONLINE")
                
                elif current_state in ["PROCESSING", "SPEAKING"]:
                    # Processing states - wait for completion
                    pass
                
                # Small sleep to prevent CPU overload
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Backend thread error: {e}")
                # Force return to ONLINE on error
                self.set_state("ONLINE")
                time.sleep(1)
    
    def attempt_auto_listen(self):
        """Attempt auto-listening without hotword"""
        try:
            current_time = datetime.now()
            hour = current_time.hour
            
            # Don't auto-listen during late night
            if 23 <= hour or hour < 7:
                return
            
            # Quick listening attempt
            command = self.safe_listen(timeout=3)
            if command and len(command.strip()) > 3:
                logger.info(f"Auto-listen command: {command}")
                self.command_received.emit(f"[Auto] {command}")
                self.process_command_safe(command)
                
        except Exception as e:
            # Silent fail for auto-listen
            pass
    
    def process_command_safe(self, command: str):
        """Safe command processing with timeout"""
        if not command or len(command.strip()) < 2:
            self.set_state("ONLINE")
            return
        
        logger.info(f"Processing command: {command}")
        self.last_command_time = time.time()
        self.set_state("PROCESSING")
        
        # Use thread for processing
        processing_thread = threading.Thread(
            target=self._process_command_thread_safe,
            args=(command,),
            daemon=True
        )
        processing_thread.start()
    
    def _process_command_thread_safe(self, command: str):
        """Thread-safe command processing"""
        try:
            if not self.jarvis_instance:
                self.set_state("ONLINE")
                return
            
            # Process command
            if hasattr(self.jarvis_instance, 'process_command'):
                response = self.jarvis_instance.process_command(command)
                
                # Check for session end
                if response == "SESSION_END" or "goodbye" in response.lower():
                    self.response_ready.emit(response)
                    time.sleep(1)
                    self.set_state("ONLINE")
                    return
                
                # Emit response
                self.response_ready.emit(response)
                
                # Speak if needed
                if (hasattr(self.jarvis_instance, 'speak') and 
                    response and len(response.strip()) > 0):
                    
                    self.set_state("SPEAKING")
                    try:
                        self.jarvis_instance.speak(response)
                        # Calculate speaking time
                        word_count = len(response.split())
                        speak_time = min(word_count * 0.12, 4)  # Max 4 seconds
                        time.sleep(speak_time)
                    except Exception as e:
                        logger.error(f"Speak error: {e}")
                
                # Return to ONLINE
                self.set_state("ONLINE")
                
            else:
                logger.error("No process_command method")
                self.response_ready.emit("System error: Processing unavailable")
                self.set_state("ONLINE")
                
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            self.response_ready.emit(f"Error: {str(e)[:50]}")
            self.set_state("ONLINE")
    
    def process_queued_commands_safe(self):
        """Process queued commands safely"""
        try:
            if not self.command_queue.empty() and self.current_state == "ONLINE":
                command = self.command_queue.get_nowait()
                logger.info(f"Processing queued command: {command}")
                self.process_command_safe(command)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
    
    def send_command(self, command: str):
        """Send command to JARVIS"""
        logger.info(f"Queueing command: {command}")
        self.command_queue.put(command)
        
        # Process immediately if in ONLINE state
        if self.current_state == "ONLINE":
            self.process_queued_commands_safe()
    
    def stop(self):
        """Stop backend thread"""
        self.running = False
        if self.force_return_timer:
            self.force_return_timer.cancel()
        self.wait()

# ============================================================================
# FIXED IRON MAN HUD INTERFACE WITH IMPROVED STATE MANAGEMENT
# ============================================================================
class IronManHUD(QMainWindow):
    """Complete Iron Man HUD Interface"""
    
    def __init__(self, backend, sound_system):
        super().__init__()
        self.backend = backend
        self.sound = sound_system
        self.voice_active = True
        
        # Window setup for transparent overlay
        self.setup_hud_window()
        
        # Initialize all HUD components
        self.init_hud_components()
        
        # Connect signals
        self.connect_signals()
        
        # Start system monitoring
        self.start_monitoring()
        
        # Auto-return to ONLINE state timer
        self.auto_return_timer = QTimer()
        self.auto_return_timer.timeout.connect(self.check_state_timeout)
        self.auto_return_timer.start(10000)  # Check every 10 seconds
        
        logger.info("Iron Man HUD initialized")
    def setup_hud_window(self):
        """Setup transparent HUD window"""
        self.setWindowTitle("JARVIS - IRON MAN HUD")
        
        # Transparent, always on top, frameless
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Semi-transparent dark background
        self.setStyleSheet("""
            QMainWindow {
                background: rgba(5, 10, 20, 30);
            }
        """)
        
        # Full screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Central widget
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(self.central_widget)
    
    def init_hud_components(self):
        """Initialize all HUD components"""
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # Top Status Bar
        self.create_status_bar()
        
        # Main Content Area
        self.create_main_content()
        
        # Bottom Control Panel
        self.create_control_panel()
    
    def create_status_bar(self):
        """Create top status bar"""
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(50)
        self.status_bar.setStyleSheet("""
            QFrame {
                background: rgba(0, 20, 40, 200);
                border: 2px solid rgba(0, 150, 255, 100);
                border-radius: 8px;
            }
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Consolas';
                background: transparent;
            }
        """)
        
        # Date
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                color: #80D0FF;
                font-size: 12px;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        
        # System Stats
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")
        
        for label in [self.cpu_label, self.ram_label]:
            label.setStyleSheet("""
                QLabel {
                    color: #00FF00;
                    font-size: 11px;
                    font-family: 'Consolas';
                    background: rgba(0, 30, 60, 150);
                    padding: 4px 10px;
                    border-radius: 4px;
                    border: 1px solid rgba(0, 150, 255, 80);
                    margin-left: 5px;
                }
            """)
        
        # Status indicator
        self.status_indicator = QLabel("ONLINE")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Arial';
                background: rgba(0, 40, 0, 150);
                padding: 4px 12px;
                border-radius: 4px;
                border: 1px solid rgba(0, 255, 0, 100);
            }
        """)
        
        status_layout.addWidget(self.time_label)
        status_layout.addWidget(self.date_label)
        status_layout.addStretch()
        status_layout.addWidget(self.cpu_label)
        status_layout.addWidget(self.ram_label)
        status_layout.addWidget(self.status_indicator)
        
        self.main_layout.addWidget(self.status_bar)
        
        # Update time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
    
    def create_main_content(self):
        """Create main content area"""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 10, 0, 10)
        content_layout.setSpacing(20)
        
        # Left Panel - System Info
        self.create_system_panel(content_layout)
        
        # Center - Chat Interface
        self.create_chat_panel(content_layout)
        
        # Right Panel - Quick Actions
        self.create_actions_panel(content_layout)
        
        self.main_layout.addWidget(content_widget, 1)
    
    def create_system_panel(self, parent_layout):
        """Create system info panel"""
        system_panel = QFrame()
        system_panel.setMaximumWidth(300)
        system_panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 25, 45, 180);
                border: 2px solid rgba(0, 150, 255, 80);
                border-radius: 10px;
            }
        """)
        
        system_layout = QVBoxLayout(system_panel)
        system_layout.setContentsMargins(15, 15, 15, 15)
        system_layout.setSpacing(10)
        
        # Title
        title = QLabel("SYSTEM STATUS")
        title.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        system_layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 100);
            }
        """)
        system_layout.addWidget(separator)
        
        # Arc Reactor Visualization - FIXED: No arguments needed
        self.arc_reactor = ArcReactorWidget()
        system_layout.addWidget(self.arc_reactor)
        
        # System Info
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setMaximumHeight(150)
        self.system_info.setStyleSheet("""
            QTextEdit {
                background: rgba(5, 15, 30, 180);
                border: 1px solid rgba(0, 100, 200, 80);
                border-radius: 5px;
                color: #80D0FF;
                font-family: 'Consolas';
                font-size: 10px;
                padding: 10px;
            }
        """)
        system_layout.addWidget(self.system_info)
        
        system_layout.addStretch()
        parent_layout.addWidget(system_panel)
    
    def create_chat_panel(self, parent_layout):
        """Create chat and command panel"""
        chat_panel = QFrame()
        chat_panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 25, 45, 180);
                border: 2px solid rgba(0, 150, 255, 80);
                border-radius: 10px;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(10)
        
        # Title
        title = QLabel("COMMAND INTERFACE")
        title.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        chat_layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 100);
            }
        """)
        chat_layout.addWidget(separator)
        
        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(5, 15, 30, 180);
                border: 1px solid rgba(0, 100, 200, 80);
                border-radius: 5px;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 10px;
            }
        """)
        chat_layout.addWidget(self.chat_display, 1)
        
        # Command Input Area
        input_frame = QFrame()
        input_frame.setFixedHeight(60)
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(20, 40, 70, 150);
                border: 1px solid rgba(0, 150, 255, 100);
                border-radius: 5px;
            }
        """)
        
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        # Voice Button
        self.voice_btn = QPushButton("Voice")
        self.voice_btn.setFixedSize(50, 40)
        self.voice_btn.setCheckable(True)
        self.voice_btn.setChecked(True)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 200, 100, 200),
                    stop:1 rgba(0, 100, 50, 150));
                border: 2px solid #00FF80;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 150, 250),
                    stop:1 rgba(0, 150, 100, 200));
                border: 2px solid #00FFCC;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 180, 250),
                    stop:1 rgba(0, 180, 120, 200));
            }
        """)
        self.voice_btn.clicked.connect(self.toggle_voice)
        input_layout.addWidget(self.voice_btn)
        
        # Command Input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command or say 'Jarvis'...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 50, 80, 200);
                border: 1px solid rgba(0, 150, 255, 100);
                border-radius: 5px;
                padding: 10px;
                color: #00FFFF;
                font-size: 13px;
            }
        """)
        self.command_input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.command_input, 1)
        
        # Send Button
        send_btn = QPushButton("Send")
        send_btn.setFixedSize(50, 40)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 200, 255, 200),
                    stop:1 rgba(0, 100, 200, 150));
                border: 2px solid #00FFFF;
                border-radius: 20px;
                color: #00FFFF;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 255, 250),
                    stop:1 rgba(0, 150, 255, 200));
            }
        """)
        send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(send_btn)
        
        chat_layout.addWidget(input_frame)
        
        parent_layout.addWidget(chat_panel, 2)
    
    def create_actions_panel(self, parent_layout):
        """Create quick actions panel"""
        actions_panel = QFrame()
        actions_panel.setMaximumWidth(300)
        actions_panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 25, 45, 180);
                border: 2px solid rgba(0, 150, 255, 80);
                border-radius: 10px;
            }
        """)
        
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(10)
        
        # Title
        title = QLabel("QUICK ACTIONS")
        title.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        actions_layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 100);
            }
        """)
        actions_layout.addWidget(separator)
        
        # Action buttons grid
        actions_grid = QGridLayout()
        actions_grid.setSpacing(10)
        
        actions = [
            ("Web", self.cmd_web),
            ("Apps", self.cmd_apps),
            ("Messages", self.cmd_message),
            ("Call", self.cmd_call),
            ("Music", self.cmd_music),
            ("Files", self.cmd_files),
            ("Settings", self.cmd_settings),
            ("Lock", self.cmd_lock)
        ]
        
        for i, (text, func) in enumerate(actions):
            btn = QPushButton(f"{text}")
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 50, 100, 150);
                    border: 1px solid rgba(0, 150, 255, 80);
                    border-radius: 5px;
                    color: #00FFFF;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(0, 100, 200, 200);
                    border: 1px solid rgba(0, 200, 255, 150);
                    color: #FFFFFF;
                }
            """)
            btn.clicked.connect(func)
            actions_grid.addWidget(btn, i // 2, i % 2)
        
        actions_layout.addLayout(actions_grid)
        actions_layout.addStretch()
        
        parent_layout.addWidget(actions_panel)
    
    def create_control_panel(self):
        """Create bottom control panel"""
        control_panel = QFrame()
        control_panel.setFixedHeight(50)
        control_panel.setStyleSheet("""
            QFrame {
                background: rgba(0, 20, 40, 200);
                border: 2px solid rgba(0, 150, 255, 80);
                border-radius: 8px;
            }
        """)
        
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 5, 15, 5)
        
        # Control buttons
        controls = [
            ("Refresh", "Refresh", self.refresh_system),
            ("Stats", "Stats", self.show_stats),
            ("Boost", "Boost", self.boost_mode),
            ("Secure", "Security", self.security_mode),
            ("Launch", "Launch", self.launch_app)
        ]
        
        for icon, tooltip, func in controls:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(70, 35)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 50, 100, 150);
                    border: 1px solid rgba(0, 150, 255, 80);
                    border-radius: 5px;
                    color: #00FFFF;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(0, 100, 200, 200);
                    border: 1px solid rgba(0, 200, 255, 150);
                    color: #FFFFFF;
                }
            """)
            btn.clicked.connect(func)
            control_layout.addWidget(btn)
        
        control_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 50, 50, 150);
                border: 1px solid rgba(255, 100, 100, 100);
                border-radius: 5px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 80, 80, 200);
                border: 1px solid rgba(255, 150, 150, 150);
            }
        """)
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)
        
        self.main_layout.addWidget(control_panel)
    
    def connect_signals(self):
        """Connect backend signals"""
        self.backend.state_changed.connect(self.handle_state_change)
        self.backend.command_received.connect(self.handle_voice_command)
        self.backend.response_ready.connect(self.handle_response)
        self.backend.hotword_detected.connect(self.handle_hotword)
        self.backend.error_occurred.connect(self.handle_error)
    
    def handle_state_change(self, state):
        """Handle system state changes"""
        logger.info(f"State change: {state}")
        
        # Remove this duplicate line:
        # logger.info(f"State change: {state}")
        
        # Add state tracking
        if not hasattr(self, 'last_state_change_time'):
            self.last_state_change_time = time.time()
        else:
            self.last_state_change_time = time.time()
        
        # Update status indicator
        status_colors = {
            "ONLINE": ("#00FF00", "ONLINE"),
            "LISTENING": ("#00FFFF", "LISTENING"),
            "PROCESSING": ("#FFA500", "PROCESSING"),
            "SPEAKING": ("#00CCFF", "SPEAKING"),
            "DEMO_MODE": ("#FF00FF", "DEMO MODE")
        }
        
        if state in status_colors:
            color, text = status_colors[state]
            self.status_indicator.setText(text)
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 12px;
                    font-weight: bold;
                    font-family: 'Arial';
                    background: rgba(20, 20, 30, 180);
                    padding: 4px 12px;
                    border-radius: 4px;
                    border: 1px solid {color};
                }}
            """)
        
        # Update arc reactor
        if hasattr(self, 'arc_reactor'):
            self.arc_reactor.set_state(state)
        
        # Auto-clear command input when returning to ONLINE
        if state == "ONLINE" and self.command_input.text():
            self.command_input.clear()
        
        # Play sound for state changes
        if state == "LISTENING" and SOUND_ENABLED:
            self.sound.play_sound("hud_activate", volume=0.5)
        elif state == "ONLINE" and SOUND_ENABLED:
            self.sound.play_sound("success", volume=0.3)
    
    def check_state_timeout(self):
        """Check if state has been stuck too long"""
        current_state = self.status_indicator.text()
        current_time = time.time()
        
        # Get last state change time (you need to track this)
        if hasattr(self, 'last_state_change_time'):
            time_in_state = current_time - self.last_state_change_time
            
            # Force return if stuck too long
            if time_in_state > 10:  # 10 seconds timeout
                logger.warning(f"State {current_state} stuck for {time_in_state:.1f}s, forcing ONLINE")
                
                # Send reset command to backend
                if hasattr(self.backend, 'set_state'):
                    self.backend.set_state("ONLINE")
                else:
                    self.handle_state_change("ONLINE")
    
    def _append_html_to_chat(self, html):
        """Append HTML to the END of chat display, ensuring sequential order."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html)
        # Add a newline after the inserted block for separation
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText("\n")
        self.scroll_chat()
    
    def handle_hotword(self):
        """Handle hotword detection"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba(255, 255, 0, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: #FFFF00;'>Hotword detected, listening for command...</span>
        </div>
        """
        self._append_html_to_chat(html)
    
    def handle_voice_command(self, command):
        """Handle voice command"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba(0, 255, 0, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: #00FF00;'>You:</span>
            <span style='color: #FFFFFF;'>{command}</span>
        </div>
        """
        self._append_html_to_chat(html)
        self.command_input.setText(command)
    
    def handle_response(self, response):
        """Handle JARVIS response"""
        if not response:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba(0, 150, 255, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: #00CCFF;'>JARVIS:</span>
            <span style='color: #FFFFFF;'>{response}</span>
        </div>
        """
        self._append_html_to_chat(html)
    
    def handle_error(self, error):
        """Handle error"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba(255, 0, 0, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: #FF0000;'>ERROR:</span>
            <span style='color: #FFFFFF;'>{error}</span>
        </div>
        """
        self._append_html_to_chat(html)
    
    def send_command(self):
        """Send command to JARVIS"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.command_input.clear()
        
        # Add to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba(0, 100, 200, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: #00AAFF;'>Text Command:</span>
            <span style='color: #FFFFFF;'>{command}</span>
        </div>
        """
        self._append_html_to_chat(html)
        
        # Send to backend
        self.backend.send_command(command)
    
    def toggle_voice(self):
        """Toggle voice listening"""
        self.voice_active = not self.voice_active
        
        if self.voice_active:
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(0, 200, 100, 200),
                        stop:1 rgba(0, 100, 50, 150));
                    border: 2px solid #00FF80;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(0, 255, 180, 250),
                        stop:1 rgba(0, 180, 120, 200));
                }
            """)
            self.add_chat_message("SYSTEM", "Voice listening enabled", "#00FF00")
        else:
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(200, 50, 50, 200),
                        stop:1 rgba(100, 25, 25, 150));
                    border: 2px solid #FF0000;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(255, 100, 100, 250),
                        stop:1 rgba(150, 50, 50, 200));
                }
            """)
            self.add_chat_message("SYSTEM", "Voice listening disabled", "#FF0000")
    
    def update_time(self):
        """Update time display"""
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%a, %b %d %Y"))
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_info)
        self.monitor_timer.start(2000)
        self.update_system_info()
    
    def update_system_info(self):
        """Update system information"""
        try:
            # CPU
            cpu = psutil.cpu_percent(interval=0.1)
            self.cpu_label.setText(f"CPU: {cpu:.0f}%")
            
            # RAM
            ram = psutil.virtual_memory().percent
            self.ram_label.setText(f"RAM: {ram:.0f}%")
            
            # Update system info text
            disk = psutil.disk_usage('/')
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            info = f"""
╔══════════════════════════╗
║     SYSTEM STATUS        ║
╠══════════════════════════╣
║ CPU:    {cpu:6.1f}%           ║
║ RAM:    {ram:6.1f}%           ║
║ Disk:   {disk.percent:6.1f}%           ║
║ Uptime: {days}d {hours:02d}:{minutes:02d}      ║
║ Processes: {len(psutil.pids()):6d}           ║
╚══════════════════════════╝
            """
            self.system_info.setPlainText(info.strip())
            
        except Exception as e:
            logger.error(f"System monitor error: {e}")
    
    def scroll_chat(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    # Quick action methods
    def cmd_web(self):
        self.send_quick_command("open browser")
    
    def cmd_apps(self):
        self.send_quick_command("open apps")
    
    def cmd_message(self):
        self.send_quick_command("open messages")
    
    def cmd_call(self):
        self.send_quick_command("make call")
    
    def cmd_music(self):
        self.send_quick_command("play music")
    
    def cmd_files(self):
        self.send_quick_command("open files")
    
    def cmd_settings(self):
        self.send_quick_command("open settings")
    
    def cmd_lock(self):
        self.send_quick_command("lock system")
    
    def send_quick_command(self, command):
        """Send quick command"""
        self.command_input.setText(command)
        self.send_command()
    
    def refresh_system(self):
        self.update_system_info()
        self.add_chat_message("SYSTEM", "System refreshed", "#00FFFF")
    
    def show_stats(self):
        self.add_chat_message("SYSTEM", "Displaying statistics...", "#00FFFF")
    
    def boost_mode(self):
        self.add_chat_message("SYSTEM", "Performance boost activated", "#00FF00")
    
    def security_mode(self):
        self.add_chat_message("SYSTEM", "Security systems engaged", "#FF0000")
    
    def launch_app(self):
        self.add_chat_message("SYSTEM", "Launching application...", "#00FFFF")
    
    def add_chat_message(self, sender, message, color):
        """Helper to add chat messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Convert hex color to RGB for background rgba()
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        except (ValueError, IndexError):
            r, g, b = 0, 150, 255
        html = f"""
        <div style='margin: 5px 0; padding: 5px; background: rgba({r}, {g}, {b}, 0.1); border-radius: 3px;'>
            <span style='color: #AAAAAA; font-size: 9px;'>[{timestamp}]</span>
            <span style='color: {color};'>{sender}:</span>
            <span style='color: #FFFFFF;'>{message}</span>
        </div>
        """
        self._append_html_to_chat(html)
    
    def closeEvent(self, event):
        """Handle window close"""
        logger.info("Shutting down Iron Man HUD")
        self.auto_return_timer.stop()
        self.backend.stop()
        event.accept()

# ============================================================================
# ARC REACTOR WIDGET (FIXED)
# ============================================================================
class ArcReactorWidget(QWidget):
    """Arc Reactor Visualization - SIMPLIFIED VERSION"""
    
    def __init__(self):
        super().__init__()
        self.state = "ONLINE"
        self.rotation = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.setMinimumHeight(200)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
    
    def set_state(self, state):
        self.state = state
    
    def animate(self):
        self.rotation = (self.rotation + 1) % 360
        self.pulse += 0.03 * self.pulse_dir
        if self.pulse >= 1.0 or self.pulse <= 0.0:
            self.pulse_dir *= -1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 4
        
        # Determine color based on state
        if self.state == "ONLINE":
            color = QColor(0, 255, 255)
        elif self.state == "LISTENING":
            color = QColor(0, 255, 100)
        elif self.state == "PROCESSING":
            color = QColor(255, 200, 0)
        elif self.state == "SPEAKING":
            color = QColor(0, 200, 255)
        else:
            color = QColor(100, 150, 200)
        
        # Outer glow
        glow_radius = radius * 2
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius)
        glow_gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 50))
        glow_gradient.setColorAt(1, Qt.transparent)
        
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - glow_radius, center_y - glow_radius,
                          glow_radius * 2, glow_radius * 2)
        
        # Rotating rings
        rings = [
            {'radius': radius, 'segments': 8, 'thickness': 3, 'speed': 1.0},
            {'radius': radius + 20, 'segments': 12, 'thickness': 2, 'speed': -1.5},
            {'radius': radius - 15, 'segments': 6, 'thickness': 2, 'speed': 0.8}
        ]
        
        for ring in rings:
            r_radius = ring['radius']
            segments = ring['segments']
            thickness = ring['thickness']
            rotation = self.rotation * ring['speed']
            
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(rotation)
            
            for seg in range(segments):
                if seg % 2 == 0:
                    painter.save()
                    painter.rotate((360 / segments) * seg)
                    
                    pen = QPen(color, thickness)
                    pen.setCapStyle(Qt.RoundCap)
                    painter.setPen(pen)
                    
                    segment_length = 15 + thickness * 2
                    painter.drawLine(r_radius - segment_length//2, 0,
                                   r_radius + segment_length//2, 0)
                    
                    painter.restore()
            
            painter.restore()
        
        # Central core
        core_size = int(radius // 2 * (0.7 + self.pulse * 0.6))
        
        if core_size > 0:
            core_gradient = QRadialGradient(center_x, center_y, core_size)
            core_gradient.setColorAt(0, QColor(255, 255, 255, 255))
            core_gradient.setColorAt(0.2, color.lighter(150))
            core_gradient.setColorAt(0.5, color)
            core_gradient.setColorAt(1, Qt.transparent)
            
            painter.setBrush(QBrush(core_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_x - core_size, center_y - core_size,
                              core_size * 2, core_size * 2)
        
        # State text
        painter.setPen(color)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRect(0, height - 25, width, 25),
                        Qt.AlignCenter, f"ARC REACTOR - {self.state}")
# ============================================================================
# MAIN APPLICATION
# ============================================================================
# ============================================================================
# UPDATED MAIN APPLICATION
# ============================================================================
class JarvisUltimateApp:
    """Main JARVIS Ultimate Application with proper backend connection"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Initialize systems
        self.sound_system = IronManSoundSystem()
        
        # Create the REAL JARVIS instance from main logic
        logger.info("Initializing JARVIS MARK I ENHANCED core...")
        self.jarvis_core = JarvisMarkIEnhanced()
        logger.info("✅ JARVIS core initialized")
        
        # Initialize backend integrator
        self.backend_integrator = JarvisBackendIntegrator()
        
        # Connect JARVIS instance to backend
        self.backend_integrator.connect_to_jarvis(self.jarvis_core)
        
        # Start with splash screen
        self.splash_screen = StarkSplashScreen(self.sound_system)
        self.splash_screen.finished.connect(self.start_hud)
        
        # Start backend
        self.backend_integrator.start()
        
        logger.info("JARVIS Ultimate Application initialized with real JARVIS core")
    
    def start_hud(self):
        """Start HUD interface"""
        # Create and show HUD
        self.hud = IronManHUD(self.backend_integrator, self.sound_system)
        
        # Add welcome message
        welcome_html = f"""
        <div style='margin: 10px 0; padding: 10px; background: rgba(0, 100, 200, 0.2); border-radius: 5px;'>
            <div style='color: #00FFFF; font-size: 14px; font-weight: bold;'>
                ⚡ JARVIS MARK I ENHANCED - ULTIMATE EDITION ⚡
            </div>
            <div style='color: #80D0FF; font-size: 11px; margin-top: 5px;'>
                Core Systems: <span style='color: #00FF00;'>ONLINE</span><br>
                Music System: <span style='color: {'#00FF00' if YOUTUBE_DL_AVAILABLE else '#FF0000'};'>{'READY' if YOUTUBE_DL_AVAILABLE else 'LIMITED'}</span><br>
                Voice: <span style='color: #00FF00;'>HUMAN-LIKE MODE</span><br>
                Voice Listening: <span style='color: #00FF00;'>ACTIVE</span>
            </div>
            <div style='color: #AAAAAA; font-size: 10px; margin-top: 5px;'>
                <b>Quick Commands:</b> play [song name], open browser, what time is it, weather, 
                open whatsapp, make call, search for [query], create file, system info
            </div>
            <div style='color: #FFA500; font-size: 10px; margin-top: 5px;'>
                <b>Music Commands:</b> play music, pause music, volume up, what's playing, trending music
            </div>
        </div>
        """
        self.hud.chat_display.insertHtml(welcome_html)
        
        # Play startup sound
        if SOUND_ENABLED:
            self.sound_system.play_sound("hud_activate", volume=0.8)
        
        # Show HUD
        self.hud.show()
    
    def run(self):
        """Run the application"""
        # Show splash screen
        self.splash_screen.show()
        
        # Run application
        return self.app.exec_()
    
    def shutdown(self):
        """Shutdown application"""
        logger.info("Shutting down JARVIS Ultimate")
        
        if hasattr(self, 'hud'):
            self.hud.close()
        
        if hasattr(self, 'splash_screen'):
            self.splash_screen.close()
        
        self.backend_integrator.stop()
        
        # Shutdown JARVIS core
        if hasattr(self.jarvis_core, 'shutdown'):
            self.jarvis_core.shutdown()
        
        if SOUND_ENABLED:
            pygame.mixer.quit()
# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗    ██████╗ ██╗   ██╗║
    ║   ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ██╔══██╗██║   ██║║
    ║   ██║███████║██████╔╝██║   ██║██║███████╗    ██║  ██║██║   ██║║
    ║   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ██║  ██║██║   ██║║
    ║   ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║    ██████╔╝╚██████╔╝║
    ║   ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ║
    ║                                                              ║
    ║     ULTIMATE CINEMATIC DESKTOP OVERLAY - IRON MAN HUD        ║
    ║          Created by Singh Industries - 2024                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Create and run application
        jarvis_app = JarvisUltimateApp()
        exit_code = jarvis_app.run()
        jarvis_app.shutdown()
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the log file: jarvis_ultimate.log")
         
        # Try to show error in message box
        try:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("JARVIS Ultimate - Fatal Error")
            error_box.setText(f"A fatal error occurred:\n\n{str(e)}\n\nCheck jarvis_ultimate.log for details.")
            error_box.exec_()
        except:
            pass
        
        sys.exit(1)