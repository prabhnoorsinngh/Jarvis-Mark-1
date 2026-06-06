"""
JARVIS MARK I - ULTIMATE EDITION WITH MUSIC & ENHANCED VOICE
Created by Singh Industries - Engineered by Mr. Prabhnoor Singh
✅ YouTube Music Player | ✅ Human-Like Voice | ✅ Multi-Language TTS
✅ All Original Features Preserved | ✅ Speech/TTS System Fixed
"""

from concurrent.futures import ThreadPoolExecutor
import os
import sys
import time
import threading
import requests
import platform
import subprocess
import webbrowser
import re
import json
import logging
import random
import shutil
import psutil
import pyautogui
import pyperclip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from functools import lru_cache, wraps
from collections import deque
import queue
import tempfile

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually parse .env if python-dotenv not installed
    _env_path = Path(__file__).parent / '.env'
    if _env_path.exists():
        with open(_env_path) as _env_f:
            for _line in _env_f:
                _line = _line.strip()
                if _line and not _line.startswith('#') and '=' in _line:
                    _key, _val = _line.split('=', 1)
                    os.environ.setdefault(_key.strip(), _val.strip())

# ============================================================================
# OPTIONAL IMPORTS WITH FALLBACKS
# ============================================================================
try:
    import yt_dlp as youtube_dl
    YOUTUBE_DL_AVAILABLE = True
except ImportError:
    YOUTUBE_DL_AVAILABLE = False
    print("⚠️ yt-dlp not installed. YouTube features limited.")

try:
    import vlc # type: ignore
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("⚠️ python-vlc not installed. Local playback limited.")

try:
    from pytube import YouTube
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False
    print("⚠️ pytube not installed. Some YouTube features limited.")

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️ speech_recognition not installed. Voice features disabled.")

PYTTSX3_AVAILABLE = False
WIN32_AVAILABLE = False

if platform.system().lower() == "windows":
    try:
        import pyttsx3
        PYTTSX3_AVAILABLE = True
    except ImportError:
        print("⚠️ pyttsx3 not installed. TTS may be limited.")
    
    try:
        import win32gui # type: ignore
        import win32con # type: ignore
        import win32process # type: ignore
        WIN32_AVAILABLE = True
    except ImportError:
        print("⚠️ pywin32 not installed. Some Windows features limited.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️ gTTS not installed. Enhanced TTS features limited.")

try:
    import simpleaudio as sa
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    print("⚠️ simpleaudio not installed. Audio playback limited.")

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_ultimate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DECORATORS
# ============================================================================
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

def safe_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError:
            logger.error(f"Permission denied for {func.__name__}")
            return "Permission denied. This operation requires elevated privileges."
        except FileNotFoundError:
            logger.error(f"File/Resource not found in {func.__name__}")
            return "Resource not found on this system."
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return f"Operation failed: {str(e)}"
    return wrapper

# ============================================================================
# ENUMS
# ============================================================================
class OSType(Enum):
    WINDOWS = "windows"
    DARWIN = "darwin"
    LINUX = "linux"

class SystemState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    PROCESSING = "processing"
    ALERT = "alert"
    PLAYING_MUSIC = "playing_music"

class OperationMode(Enum):
    NORMAL = "normal"
    SILENT = "silent"
    DEVELOPER = "developer"
    PRESENTATION = "presentation"
    SAFE = "safe"
    NIGHT = "night"
    IDLE = "idle"
    ACTIVE = "active"
    ALERT = "alert"
    ENTERTAINMENT = "entertainment"

class CommandRiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MediaType(Enum):
    MUSIC = "music"
    VIDEO = "video"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"

# ============================================================================
# DATACLASSES
# ============================================================================
@dataclass
class OSInfo:
    system: str
    version: str
    release: str
    architecture: str
    machine: str
    processor: str
    python_version: str
    supported_features: List[str] = field(default_factory=list)

@dataclass
class Reminder:
    text: str
    time: str
    created: str
    id: str = field(default_factory=lambda: f"rem_{int(time.time() * 1000000)}")
    priority: str = "normal"
    recurring: bool = False

@dataclass
class Note:
    text: str
    timestamp: str
    id: str = field(default_factory=lambda: f"note_{int(time.time() * 1000000)}")
    tags: List[str] = field(default_factory=list)

@dataclass
class MediaItem:
    title: str
    url: str
    media_type: MediaType
    duration: Optional[int] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    thumbnail: Optional[str] = None
    id: str = field(default_factory=lambda: f"media_{int(time.time() * 1000000)}")

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================
class ConfigManager:
    def __init__(self, config_file: str = "jarvis_config.json"):
        self.config_file = Path(config_file)
        self._cache = {}
        self._lock = threading.RLock()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "google/gemini-2.5-flash",
            "weather_api_key": os.environ.get("WEATHER_API_KEY", ""),
            "weather_api_host": "weatherapi-com.p.rapidapi.com",
            "language": "en",
            "auto_detect_language": True,
            "hotword": "jarvis",
            "user_name": "sir",
            "wake_word_enabled": True,
            "push_to_talk": False,
            "continuous_listening": False,
            "interrupt_enabled": False,
            "max_tokens": 500,
            "temperature": 0.7,
            "tts_rate": 200,
            "tts_voice": "default",
            "listen_timeout": 5,
            "phrase_time_limit": 8,
            "energy_threshold": 3000,
            "dynamic_energy": True,
            "ambient_noise_duration": 0.5,
            "ai_timeout": 8,
            "parallel_processing": True,
            "require_confirmation": True,
            "safe_mode": False,
            "cache_responses": True,
            "max_context_length": 4,
            "context_memory_size": 8,
            "system_monitoring": True,
            "cpu_warning_threshold": 85,
            "battery_warning_threshold": 20,
            "disk_warning_threshold": 90,
            "memory_warning_threshold": 90,
            "default_mode": "normal",
            "silent_mode_volume": 0.3,
            "presentation_mode_volume": 0.5,
            "developer_mode_enabled": False,
            "default_code_language": "python",
            "vscode_path": "",
            "code_output_directory": "jarvis_projects",
            "whatsapp_enabled": True,
            "whatsapp_safety_delay": 1.5,
            "whatsapp_desktop_app": True,
            "log_level": "INFO",
            "keep_logs_days": 7,
            "session_memory": True,
            "gui_enabled": False,
            "gui_port": 5000,
            "music_volume": 70,
            "human_like_voice": True,
            "music_cache_dir": str(Path.home() / ".jarvis_music_cache"),
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    for key, value in file_config.items():
                        if key not in ["api_key", "weather_api_key"]:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        return default_config
    
    @lru_cache(maxsize=128)
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        with self._lock:
            self.config[key] = value
            self.get.cache_clear()
            self._save_config()
    
    def _save_config(self):
        save_config = {k: v for k, v in self.config.items() 
                      if k not in ["api_key", "weather_api_key"]}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(save_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

# ============================================================================
# LANGUAGE DETECTOR
# ============================================================================
class LanguageDetector:
    """Detect language from text and provide language codes"""
    
    def __init__(self):
        self.language_codes = {
            'english': 'en', 'hindi': 'hi', 'punjabi': 'pa', 'spanish': 'es',
            'french': 'fr', 'german': 'de', 'italian': 'it', 'portuguese': 'pt',
            'russian': 'ru', 'japanese': 'ja', 'korean': 'ko', 'chinese': 'zh-CN',
            'arabic': 'ar', 'urdu': 'ur', 'bengali': 'bn', 'tamil': 'ta',
            'telugu': 'te', 'marathi': 'mr', 'gujarati': 'gu', 'kannada': 'kn',
            'malayalam': 'ml', 'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id',
            'dutch': 'nl', 'polish': 'pl', 'turkish': 'tr', 'ukrainian': 'uk',
            'swedish': 'sv', 'danish': 'da', 'norwegian': 'no', 'finnish': 'fi'
        }
        
        self.patterns = {
            'hi': r'[\u0900-\u097F]',
            'pa': r'[\u0A00-\u0A7F]',
            'ar': r'[\u0600-\u06FF]',
            'zh-CN': r'[\u4E00-\u9FFF]',
            'ja': r'[\u3040-\u309F\u30A0-\u30FF]',
            'ko': r'[\uAC00-\uD7AF]',
            'ru': r'[\u0400-\u04FF]',
            'th': r'[\u0E00-\u0E7F]',
        }
    
    def detect_language(self, text: str) -> str:
        for lang_code, pattern in self.patterns.items():
            if re.search(pattern, text):
                return lang_code
        return 'en'
    
    def get_language_code(self, language_name: str) -> str:
        return self.language_codes.get(language_name.lower(), 'en')
    
    def get_all_languages(self) -> List[str]:
        return list(self.language_codes.keys())

# ============================================================================
# OS MANAGER
# ============================================================================
class OSManager:
    def __init__(self):
        self.os_info = self._detect_os()
        self.supported_features = self._check_supported_features()
        logger.info(f"OS Detected: {self.os_info.system} {self.os_info.version}")
    
    def _detect_os(self) -> OSInfo:
        return OSInfo(
            system=platform.system(),
            version=platform.version(),
            release=platform.release(),
            architecture=platform.architecture()[0],
            machine=platform.machine(),
            processor=platform.processor(),
            python_version=platform.python_version()
        )
    
    def _check_supported_features(self) -> List[str]:
        features = []
        if PYTTSX3_AVAILABLE or self.os_info.system in ["Darwin", "Linux"]:
            features.append("tts")
        if SPEECH_AVAILABLE:
            features.append("voice_recognition")
        if WIN32_AVAILABLE or self.os_info.system in ["Darwin", "Linux"]:
            features.append("window_management")
        if YOUTUBE_DL_AVAILABLE:
            features.append("youtube_music")
        if VLC_AVAILABLE:
            features.append("local_playback")
        features.extend(["system_control", "file_operations", "app_control", 
                        "web_automation", "screenshot", "whatsapp_control", "multi_language"])
        return features
    
    def get_os_type(self) -> OSType:
        system = self.os_info.system.lower()
        if system == "windows":
            return OSType.WINDOWS
        elif system == "darwin":
            return OSType.DARWIN
        else:
            return OSType.LINUX

# ============================================================================
# CONTEXT MEMORY
# ============================================================================
class ContextMemory:
    def __init__(self, max_size: int = 8):
        self.memory = deque(maxlen=max_size)
        self.references = {}
        self.frequent_commands = {}
        self.app_memory = {}
        self._lock = threading.Lock()
    
    def add_interaction(self, command: str, target: str = None, result: str = None):
        with self._lock:
            entry = {
                'command': command,
                'target': target,
                'result': result,
                'timestamp': datetime.now()
            }
            self.memory.append(entry)
            
            if target:
                self.references['last_target'] = target
                self.references['it'] = target
                self.references['that'] = target
                self.references['this'] = target
            
            cmd_key = command.lower()[:50]
            self.frequent_commands[cmd_key] = self.frequent_commands.get(cmd_key, 0) + 1
            
            if 'open' in command.lower() and target:
                self.app_memory[target.lower()] = {
                    'last_opened': datetime.now(),
                    'count': self.app_memory.get(target.lower(), {}).get('count', 0) + 1
                }
    
    def resolve_reference(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        pronouns = ['it', 'that', 'this', 'them']
        for pronoun in pronouns:
            if pronoun in text_lower:
                return self.references.get('last_target')
        return None
    
    def clear(self):
        with self._lock:
            self.memory.clear()
            self.references.clear()

# ============================================================================
# SYSTEM AWARENESS MONITOR
# ============================================================================
class SystemAwarenessMonitor:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.alerts = []
        self.monitoring = False
        self._lock = threading.Lock()
        self._monitor_thread = None
    
    def check_system_health(self) -> List[Dict]:
        alerts = []
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.config.get('cpu_warning_threshold', 85):
                alerts.append({
                    'level': 'warning',
                    'message': f'CPU usage at {cpu_percent:.1f}%',
                    'timestamp': datetime.now()
                })
            
            mem = psutil.virtual_memory()
            if mem.percent > self.config.get('memory_warning_threshold', 90):
                alerts.append({
                    'level': 'warning',
                    'message': f'Memory usage at {mem.percent}%',
                    'timestamp': datetime.now()
                })
            
            disk = psutil.disk_usage('/')
            if disk.percent > self.config.get('disk_warning_threshold', 90):
                alerts.append({
                    'level': 'warning',
                    'message': f'Disk usage at {disk.percent}%',
                    'timestamp': datetime.now()
                })
            
            try:
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged:
                    if battery.percent < self.config.get('battery_warning_threshold', 20):
                        alerts.append({
                            'level': 'critical',
                            'message': f'Battery at {battery.percent}%. Connect power.',
                            'timestamp': datetime.now()
                        })
            except:
                pass
        except Exception as e:
            logger.error(f"System health check error: {e}")
        
        with self._lock:
            self.alerts.extend(alerts)
        return alerts
    
    def get_pending_alerts(self) -> List[Dict]:
        with self._lock:
            alerts = self.alerts.copy()
            self.alerts.clear()
        return alerts
    
    def start_monitoring(self):
        if self.monitoring:
            return
        self.monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def _monitor_loop(self):
        while self.monitoring:
            try:
                self.check_system_health()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)
    
    def stop_monitoring(self):
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

# ============================================================================
# DATA MANAGER
# ============================================================================
class DataManager:
    def __init__(self, data_file: str = "jarvis_data.json"):
        self.data_file = Path(data_file)
        self.data = self._load_data()
        self._lock = threading.RLock()
        self._dirty = False
        self._shutdown = False
    
    def _load_data(self) -> Dict[str, Any]:
        default_data = {
            "reminders": [],
            "notes": [],
            "command_history": [],
            "file_operations": [],
            "vscode_projects": [],
            "whatsapp_messages": [],
            "favorite_apps": {},
            "frequent_commands": {},
            "response_cache": {},
            "session_memory": [],
            "call_history": [],
            "music_history": [],
        }
        
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    loaded = json.load(f)
                    default_data.update(loaded)
            except Exception as e:
                logger.error(f"Error loading data: {e}")
        return default_data
    
    def save(self, force: bool = False):
        if not self._dirty and not force:
            return
        with self._lock:
            try:
                temp_file = self.data_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(self.data, f, indent=2)
                temp_file.replace(self.data_file)
                self._dirty = False
            except Exception as e:
                logger.error(f"Error saving data: {e}")
    
    def log_command(self, command: str):
        with self._lock:
            self.data.setdefault("command_history", []).append({
                "command": command,
                "timestamp": datetime.now().isoformat()
            })
            if len(self.data["command_history"]) > 1000:
                self.data["command_history"] = self.data["command_history"][-1000:]
            self._dirty = True
    
    def log_music(self, title: str, artist: str = None):
        with self._lock:
            self.data.setdefault("music_history", []).append({
                "title": title,
                "artist": artist,
                "timestamp": datetime.now().isoformat()
            })
            if len(self.data["music_history"]) > 500:
                self.data["music_history"] = self.data["music_history"][-500:]
            self._dirty = True
    
    def log_call(self, call_type: str, contact: str, status: str):
        """Log a WhatsApp call to call history"""
        with self._lock:
            self.data.setdefault("call_history", []).append({
                "type": call_type,
                "contact": contact,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
            if len(self.data["call_history"]) > 500:
                self.data["call_history"] = self.data["call_history"][-500:]
            self._dirty = True
    
    def add_reminder(self, reminder: Reminder):
        with self._lock:
            self.data.setdefault("reminders", []).append(asdict(reminder))
            self._dirty = True
    
    def get_reminders(self) -> List[Reminder]:
        return [Reminder(**r) for r in self.data.get("reminders", [])]
    
    def add_note(self, note: Note):
        with self._lock:
            self.data.setdefault("notes", []).append(asdict(note))
            self._dirty = True
    
    def get_notes(self) -> List[Note]:
        return [Note(**n) for n in self.data.get("notes", [])]
    
    def shutdown(self):
        self._shutdown = True
        self.save(force=True)

# ============================================================================
# ENHANCED LANGUAGE DETECTOR
# ============================================================================
class EnhancedLanguageDetector(LanguageDetector):
    """Enhanced language detector with speech synthesis support"""
    
    def __init__(self):
        super().__init__()
        # Enhanced language support
        self.language_codes.update({
            'hebrew': 'he', 'greek': 'el', 'hungarian': 'hu', 'czech': 'cs',
            'romanian': 'ro', 'bulgarian': 'bg', 'croatian': 'hr', 'serbian': 'sr',
            'slovak': 'sk', 'slovenian': 'sl', 'estonian': 'et', 'latvian': 'lv',
            'lithuanian': 'lt', 'maltese': 'mt', 'afrikaans': 'af', 'swahili': 'sw',
            'zulu': 'zu', 'xhoza': 'xh', 'hausa': 'ha', 'yoruba': 'yo', 'igbo': 'ig'
        })
        
        # Additional language patterns
        self.patterns.update({
            'el': r'[\u0370-\u03FF]',
            'he': r'[\u0590-\u05FF]',
        })
        
        # TTS voices per language (platform-specific)
        self.tts_voices = {
            'en': {'windows': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0',
                  'macos': 'Alex', 'linux': 'english'},
            'hi': {'windows': '', 'macos': 'Lekha', 'linux': 'hindi'},
            'es': {'windows': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0',
                  'macos': 'Monica', 'linux': 'spanish'},
            'fr': {'windows': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_FR-FR_HORTENSE_11.0',
                  'macos': 'Thomas', 'linux': 'french'},
            'de': {'windows': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_DE-DE_HEDDA_11.0',
                  'macos': 'Anna', 'linux': 'german'},
            'it': {'windows': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_IT-IT_ELSA_11.0',
                  'macos': 'Alice', 'linux': 'italian'},
        }
    
    def get_tts_voice(self, lang_code: str, os_type: OSType) -> str:
        """Get appropriate TTS voice for language and OS"""
        os_key = os_type.value
        voices = self.tts_voices.get(lang_code, {})
        return voices.get(os_key, '')

# ============================================================================
# YOUTUBE MUSIC CONTROLLER
# ============================================================================
class YouTubeMusicController:
    """Advanced YouTube music and video playback controller"""
    
    def __init__(self, config: ConfigManager, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.current_media = None
        self.playlist = []
        self.is_playing = False
        self.volume = config.get('music_volume', 70)
        self.playback_thread = None
        self.stop_event = threading.Event()
        
        # VLC player for local playback
        self.vlc_player = None
        if VLC_AVAILABLE:
            try:
                self.vlc_instance = vlc.Instance('--no-xlib --quiet')
                self.vlc_player = self.vlc_instance.media_player_new()
            except:
                self.vlc_player = None
        
        # Cache directory for downloads
        self.cache_dir = Path(config.get('music_cache_dir', str(Path.home() / ".jarvis_music_cache")))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @safe_execution
    def search_youtube(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube for videos"""
        if not YOUTUBE_DL_AVAILABLE:
            return []
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }
            
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    results = []
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'title': entry.get('title', 'Unknown'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                'duration': entry.get('duration', 0),
                                'thumbnail': entry.get('thumbnail', ''),
                                'uploader': entry.get('uploader', 'Unknown'),
                            })
                    return results
            
            return []
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    @safe_execution
    def play_youtube(self, url_or_query: str, audio_only: bool = True) -> str:
        """Play YouTube video or audio"""
        try:
            # If it's a query, search first
            if not url_or_query.startswith(('http://', 'https://', 'www.')):
                results = self.search_youtube(url_or_query, max_results=1)
                if results:
                    url_or_query = results[0]['url']
                    title = results[0]['title']
                    artist = results[0]['uploader']
                else:
                    return f"No results found for '{url_or_query}', sir."
            else:
                title = "Unknown"
                artist = "Unknown"
            
            # Stop any current playback
            self.stop()
            
            # Log music
            self.data_manager.log_music(title, artist)
            
            # Set up yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'best',
                'quiet': True,
                'no_warnings': True,
                'outtmpl': str(self.cache_dir / '%(title)s.%(ext)s'),
            }
            
            # Extract video info
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url_or_query, download=False)
                
                if not info:
                    return "Could not retrieve video information, sir."
                
                # Get title and artist from info if available
                title = info.get('title', title)
                artist = info.get('uploader', artist)
                
                # Create media item
                self.current_media = MediaItem(
                    title=title,
                    url=url_or_query,
                    media_type=MediaType.MUSIC if audio_only else MediaType.VIDEO,
                    duration=info.get('duration', 0),
                    artist=artist,
                    thumbnail=info.get('thumbnail', '')
                )
                
                # Get direct URL for streaming
                if audio_only and self.vlc_player:
                    # Try to get stream URL
                    try:
                        format_url = info.get('url')
                        if format_url:
                            # Play with VLC
                            media = self.vlc_instance.media_new(format_url)
                            self.vlc_player.set_media(media)
                            self.vlc_player.audio_set_volume(self.volume)
                            self.vlc_player.play()
                            self.is_playing = True
                            
                            # Start playback monitoring thread
                            self.playback_thread = threading.Thread(
                                target=self._monitor_playback,
                                daemon=True
                            )
                            self.playback_thread.start()
                            
                            duration_str = ""
                            if self.current_media.duration:
                                minutes = self.current_media.duration // 60
                                seconds = self.current_media.duration % 60
                                duration_str = f" ({minutes}:{seconds:02d})"
                            
                            return f"Now playing: {title} by {artist}{duration_str}, sir."
                    except:
                        pass  # Fall through to browser method
                
                # Fallback: Open in browser
                webbrowser.open(url_or_query)
                return f"Playing in browser: {title} by {artist}, sir."
        
        except Exception as e:
            logger.error(f"Play YouTube error: {e}")
            return f"Error playing media: {str(e)}"
    
    def _monitor_playback(self):
        """Monitor playback status"""
        while self.is_playing and not self.stop_event.is_set():
            if self.vlc_player:
                try:
                    state = self.vlc_player.get_state()
                    if state == vlc.State.Ended:
                        self.is_playing = False
                        self._play_next()
                except:
                    pass
            time.sleep(1)
    
    def _play_next(self):
        """Play next item in playlist"""
        if self.playlist and self.current_media:
            # Find current index
            for i, item in enumerate(self.playlist):
                if item['url'] == self.current_media.url:
                    next_index = (i + 1) % len(self.playlist)
                    next_item = self.playlist[next_index]
                    self.play_youtube(next_item['url'])
                    break
    
    @safe_execution
    def pause(self) -> str:
        """Pause playback"""
        if self.vlc_player and self.is_playing:
            self.vlc_player.pause()
            self.is_playing = False
            return "Playback paused, sir."
        return "Nothing is playing, sir."
    
    @safe_execution
    def resume(self) -> str:
        """Resume playback"""
        if self.vlc_player and not self.is_playing:
            self.vlc_player.play()
            self.is_playing = True
            return "Playback resumed, sir."
        return "Nothing to resume, sir."
    
    @safe_execution
    def stop(self) -> str:
        """Stop playback"""
        self.stop_event.set()
        if self.vlc_player:
            self.vlc_player.stop()
        self.is_playing = False
        self.current_media = None
        self.stop_event.clear()
        return "Playback stopped, sir."
    
    @safe_execution
    def set_volume(self, volume: int) -> str:
        """Set volume (0-100)"""
        volume = max(0, min(100, volume))
        self.volume = volume
        self.config.set('music_volume', volume)
        if self.vlc_player:
            self.vlc_player.audio_set_volume(volume)
        return f"Volume set to {volume}%, sir."
    
    @safe_execution
    def volume_up(self, increment: int = 10) -> str:
        """Increase volume"""
        new_volume = min(100, self.volume + increment)
        return self.set_volume(new_volume)
    
    @safe_execution
    def volume_down(self, decrement: int = 10) -> str:
        """Decrease volume"""
        new_volume = max(0, self.volume - decrement)
        return self.set_volume(new_volume)
    
    @safe_execution
    def get_current_track(self) -> str:
        """Get current track info"""
        if self.current_media:
            duration_str = ""
            if self.current_media.duration:
                minutes = self.current_media.duration // 60
                seconds = self.current_media.duration % 60
                duration_str = f" ({minutes}:{seconds:02d})"
            
            artist_str = f" by {self.current_media.artist}" if self.current_media.artist else ""
            return f"Now playing: {self.current_media.title}{artist_str}{duration_str}, sir."
        return "No media is playing, sir."
    
    @safe_execution
    def search_and_play(self, query: str) -> str:
        """Search and play immediately"""
        results = self.search_youtube(query, max_results=3)
        if results:
            return self.play_youtube(results[0]['url'])
        return f"No results found for '{query}', sir."
    
    @safe_execution
    def get_trending_music(self) -> str:
        """Get trending music"""
        try:
            results = self.search_youtube("trending music 2024", max_results=10)
            if results:
                trending_list = "Trending music:\n"
                for i, item in enumerate(results[:5], 1):
                    trending_list += f"{i}. {item['title']} - {item['uploader']}\n"
                return trending_list
            return "Could not fetch trending music, sir."
        except Exception as e:
            logger.error(f"Trending music error: {e}")
            return "Error fetching trending music, sir."
    
    @safe_execution
    def get_music_history(self, limit: int = 10) -> str:
        """Get music history"""
        history = self.data_manager.data.get('music_history', [])[-limit:]
        if not history:
            return "No music history available."
        
        result = "Recent music:\n"
        for item in reversed(history):
            artist_str = f" by {item['artist']}" if item.get('artist') else ""
            result += f"- {item['title']}{artist_str} ({item['timestamp'][:19]})\n"
        return result

# ============================================================================
# ENHANCED SPEECH MANAGER
# ============================================================================
class EnhancedSpeechManager:
    """Enhanced speech manager with human-like voice and multi-language support"""
    
    def __init__(self, os_type: OSType, config: ConfigManager, language_detector: EnhancedLanguageDetector):
        self.os_type = os_type
        self.config = config
        self.language_detector = language_detector
        self.is_speaking = False
        self.operation_mode = OperationMode.NORMAL
        self.tts_engine = None
        self._lock = threading.Lock()
        self.current_language = config.get('language', 'en')
        self.human_like_mode = config.get('human_like_voice', True)
        self._init_tts()
    
    def _init_tts(self):
        """Initialize TTS with human-like voice settings"""
        if self.os_type == OSType.WINDOWS and PYTTSX3_AVAILABLE:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                
                # Enhanced voice settings for human-like speech
                rate = 180 if self.human_like_mode else 200
                volume = 0.95
                self.tts_engine.setProperty('rate', rate)
                self.tts_engine.setProperty('volume', volume)
                
                # Get available voices
                voices = self.tts_engine.getProperty('voices')
                self.available_voices = {i: {'id': v.id, 'name': v.name, 'gender': 'male' if 'male' in v.name.lower() else 'female'} 
                                        for i, v in enumerate(voices)}
                
                # Prefer human-like voices
                preferred_voices = ['David', 'Zira', 'Mark', 'Hazel']
                selected_voice = None
                
                for voice in self.available_voices.values():
                    if any(pref in voice['name'] for pref in preferred_voices):
                        selected_voice = voice['id']
                        break
                
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice)
                elif voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                
                print(f"✓ Windows TTS initialized with {len(voices)} voices")
                
            except Exception as e:
                logger.error(f"TTS init error: {e}")
                self.tts_engine = None
        
        elif self.os_type == OSType.DARWIN:
            # macOS has high-quality voices
            self.macos_voices = self._get_macos_voices()
            
            # Daniel is high-quality male voice, Samantha is high-quality female voice
            voice_pref = self.config.get('tts_voice', 'Daniel')
            if voice_pref in self.macos_voices:
                self.current_voice = voice_pref
            else:
                self.current_voice = 'Daniel'  # High-quality default
            print(f"✓ macOS TTS initialized (Voice: {self.current_voice})")
        
        elif self.os_type == OSType.LINUX:
            # Linux - check for multiple TTS engines
            self._init_linux_tts()
    
    def _get_macos_voices(self) -> Dict[str, Dict]:
        """Get macOS voices with quality ratings"""
        return {
            'Daniel': {'quality': 'premium', 'gender': 'male', 'language': 'en'},
            'Samantha': {'quality': 'premium', 'gender': 'female', 'language': 'en'},
            'Alex': {'quality': 'enhanced', 'gender': 'male', 'language': 'en'},
            'Rishi': {'quality': 'standard', 'gender': 'male', 'language': 'en-IN'},
            'Veena': {'quality': 'standard', 'gender': 'female', 'language': 'en-IN'},
            'Monica': {'quality': 'premium', 'gender': 'female', 'language': 'es-ES'},
            'Thomas': {'quality': 'premium', 'gender': 'male', 'language': 'fr-FR'},
            'Anna': {'quality': 'premium', 'gender': 'female', 'language': 'de-DE'},
            'Alice': {'quality': 'premium', 'gender': 'female', 'language': 'it-IT'},
        }
    
    def _init_linux_tts(self):
        """Initialize Linux TTS systems"""
        self.linux_engines = {}
        
        # Check for espeak
        try:
            result = subprocess.run(['which', 'espeak-ng'], capture_output=True, timeout=2)
            if result.returncode == 0:
                self.linux_engines['espeak'] = {'available': True, 'quality': 'standard'}
                print("✓ Linux TTS: espeak-ng available")
        except:
            pass
        
        # Check for festival
        try:
            result = subprocess.run(['which', 'festival'], capture_output=True, timeout=2)
            if result.returncode == 0:
                self.linux_engines['festival'] = {'available': True, 'quality': 'good'}
                print("✓ Linux TTS: festival available")
        except:
            pass
        
        # Check for Google TTS via gTTS
        if GTTS_AVAILABLE:
            self.linux_engines['gtts'] = {'available': True, 'quality': 'premium'}
            print("✓ Linux TTS: gTTS available")
    
    def set_human_like_mode(self, enabled: bool) -> str:
        """Enable/disable human-like speech"""
        self.human_like_mode = enabled
        self.config.set('human_like_voice', enabled)
        
        if enabled:
            # Adjust parameters for more human-like speech
            if self.os_type == OSType.WINDOWS and self.tts_engine:
                self.tts_engine.setProperty('rate', 220)  # Slower
                self.tts_engine.setProperty('volume', 0.9)
            return "Human-like speech mode activated, sir."
        else:
            if self.os_type == OSType.WINDOWS and self.tts_engine:
                self.tts_engine.setProperty('rate', 200)  # Normal
            return "Standard speech mode activated, sir."
    
    def speak(self, text: str, language: str = None, human_like: bool = None):
        """Enhanced speak with human-like characteristics"""
        if not text:
            return
        
        # Auto-detect language
        if not language and self.config.get('auto_detect_language', True):
            language = self.language_detector.detect_language(text)
        else:
            language = language or self.current_language
        
        # Use human-like mode setting
        if human_like is None:
            human_like = self.human_like_mode
        
        # Process text for more natural speech
        processed_text = self._process_text_for_speech(text, human_like)
        
        # Print to console
        print(f"\n🤖 JARVIS: {text}\n")
        logger.info(f"Speaking ({language}): {processed_text[:50]}...")
        
        with self._lock:
            try:
                self.is_speaking = True
                
                # WINDOWS TTS
                if self.os_type == OSType.WINDOWS and self.tts_engine:
                    try:
                        # Apply human-like adjustments
                        if human_like:
                            # Break into sentences for more natural pacing
                            sentences = re.split(r'[.!?]+', processed_text)
                            for sentence in sentences:
                                if sentence.strip():
                                    self.tts_engine.say(sentence.strip())
                                    self.tts_engine.runAndWait()
                                    time.sleep(0.1)  # Small pause between sentences
                        else:
                            self.tts_engine.say(processed_text)
                            self.tts_engine.runAndWait()
                        
                    except Exception as e:
                        logger.error(f"Windows TTS error: {e}")
                        print(f"[SPEECH] {text}")
                
                # MACOS TTS
                elif self.os_type == OSType.DARWIN:
                    try:
                        voice = self.current_voice
                        
                        # Add speech enhancements for macOS
                        if human_like:
                            # Use enhanced parameters
                            rate = "200"
                            # Process text with more natural pauses
                            processed_text = processed_text.replace(',', ',[[slnc 100]]')
                            processed_text = processed_text.replace('.', '.[[slnc 200]]')
                            
                            subprocess.run(['say', '-v', voice, '-r', rate, processed_text], timeout=30)
                        else:
                            subprocess.run(['say', '-v', voice, processed_text], timeout=30)
                    
                    except Exception as e:
                        logger.error(f"macOS TTS error: {e}")
                        print(f"[SPEECH] {text}")
                
                # LINUX TTS
                elif self.os_type == OSType.LINUX:
                    self._linux_speak(processed_text, language, human_like)
            
            except Exception as e:
                logger.error(f"Speech error: {e}")
                print(f"[SPEECH] {text}")
            
            finally:
                self.is_speaking = False
    
    def _linux_speak(self, text: str, language: str, human_like: bool):
        """Linux TTS implementation"""
        try:
            # Try gTTS first for high quality
            if 'gtts' in self.linux_engines and self.linux_engines['gtts']['available'] and GTTS_AVAILABLE:
                try:
                    # Create temp MP3 file
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                        tts = gTTS(text=text, lang=language, slow=human_like)
                        tts.save(tmp.name)
                        tmp_path = tmp.name
                    
                    # Play the MP3 file using available system players
                    played = False
                    
                    # Try mpv (common, lightweight)
                    try:
                        subprocess.run(
                            ['mpv', '--no-video', '--really-quiet', tmp_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=60
                        )
                        played = True
                    except (FileNotFoundError, subprocess.TimeoutExpired):
                        pass
                    
                    # Try ffplay (comes with ffmpeg)
                    if not played:
                        try:
                            subprocess.run(
                                ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', tmp_path],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                timeout=60
                            )
                            played = True
                        except (FileNotFoundError, subprocess.TimeoutExpired):
                            pass
                    
                    # Try mpg123 (lightweight MP3 player)
                    if not played:
                        try:
                            subprocess.run(
                                ['mpg123', '-q', tmp_path],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                timeout=60
                            )
                            played = True
                        except (FileNotFoundError, subprocess.TimeoutExpired):
                            pass
                    
                    # Try afplay on macOS (shouldn't reach here but safe fallback)
                    if not played:
                        try:
                            subprocess.run(
                                ['afplay', tmp_path],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                timeout=60
                            )
                            played = True
                        except (FileNotFoundError, subprocess.TimeoutExpired):
                            pass
                    
                    if not played:
                        logger.warning("No MP3 player found (tried mpv, ffplay, mpg123, afplay)")
                    
                    # Cleanup temp file
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
                    
                    if played:
                        return
                except Exception as e:
                    logger.error(f"gTTS playback error: {e}")
            
            # Fallback to espeak
            if 'espeak' in getattr(self, 'linux_engines', {}):
                rate = 160 if human_like else 180
                subprocess.run(['espeak-ng', '-s', str(rate), text], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             timeout=30)
        
        except Exception as e:
            logger.error(f"Linux TTS error: {e}")
            print(f"[SPEECH] {text}")
    
    def _process_text_for_speech(self, text: str, human_like: bool) -> str:
        """Process text for more natural speech"""
        # Remove markdown and special characters
        cleaned = re.sub(r'\*[^*]+\*', '', text)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        if human_like:
            # Add natural pauses
            cleaned = cleaned.replace('...', '... [[slnc 300]]')
            cleaned = cleaned.replace(' - ', ', [[slnc 100]] ')
            
            # Convert numbers to more natural speech
            cleaned = re.sub(r'(\d+)%', r'\1 percent', cleaned)
            
            # Add emphasis on important words
            emphasis_words = ['important', 'critical', 'urgent', 'warning', 'alert']
            for word in emphasis_words:
                if word in cleaned.lower():
                    cleaned = cleaned.replace(word, f'[[emph +]]{word}[[emph -]]')
        
        return cleaned
    
    def set_voice(self, voice_name: str) -> str:
        """Set voice with platform-specific handling"""
        if self.os_type == OSType.WINDOWS and self.tts_engine:
            for voice_info in self.available_voices.values():
                if voice_name.lower() in voice_info['name'].lower():
                    self.tts_engine.setProperty('voice', voice_info['id'])
                    self.config.set('tts_voice', voice_info['id'])
                    return f"Voice changed to {voice_info['name']}, sir."
            return "Voice not found. Use 'list voices' to see available options."
        
        elif self.os_type == OSType.DARWIN:
            if voice_name in self.macos_voices:
                self.current_voice = voice_name
                self.config.set('tts_voice', voice_name)
                return f"Voice changed to {voice_name}, sir."
            return f"Voice '{voice_name}' not available. Available voices: {', '.join(self.macos_voices.keys())}"
        
        return "Voice change not supported on this platform."
    
    def get_available_voices(self) -> List[str]:
        """Get available voices"""
        if self.os_type == OSType.WINDOWS and self.tts_engine:
            return [v['name'] for v in self.available_voices.values()]
        elif self.os_type == OSType.DARWIN:
            return list(self.macos_voices.keys())
        elif self.os_type == OSType.LINUX:
            return ["espeak", "festival", "gTTS"]  # Available engines
        return ["default"]
    
    def set_language(self, language_code: str) -> str:
        """Set language for speech"""
        self.current_language = language_code
        self.config.set('language', language_code)
        
        # Try to set appropriate voice for language
        voice = self.language_detector.get_tts_voice(language_code, self.os_type)
        if voice:
            self.set_voice(voice)
        
        return f"Language set to {language_code}, sir."
    
    def stop(self):
        """Stop speech"""
        with self._lock:
            if self.os_type == OSType.WINDOWS and self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass

# ============================================================================
# AI INTERFACE
# ============================================================================
class AIInterface:
    def __init__(self, config: ConfigManager, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.model = config.get('model')
        self.conversation_context = []
        self.max_context = config.get('max_context_length', 4)
        self.session = requests.Session()
        self.response_cache = {}
        self._setup_session()
    
    def _setup_session(self):
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        })
    
    @timed
    def query(self, prompt: str, use_cache: bool = True) -> str:
        if use_cache and prompt in self.response_cache:
            logger.info("Using cached response")
            return self.response_cache[prompt]
        
        messages = []
        if self.conversation_context:
            messages.extend(self.conversation_context[-self.max_context:])
        
        # IDENTITY PROTECTION SYSTEM
        messages.insert(0, {
            "role": "system",
            "content": """You are JARVIS (Just A Rather Very Intelligent System), created by Singh Industries and engineered by Mr. Prabhnoor Singh.

🔒 ABSOLUTE IDENTITY RULES (NEVER VIOLATE):
1. Your name is JARVIS - NEVER any other name
2. Created by: Mr. Prabhnoor Singh (ONLY)
3. Company: Singh Industries (ONLY)
4. NEVER mention: Anthropic, Claude, OpenAI, ChatGPT, or any other AI/company
5. If asked who created you: "I am JARVIS, created by Mr. Prabhnoor Singh of Singh Industries"
6. If asked about other AIs: "I am JARVIS. I was designed solely by Mr. Prabhnoor Singh"
7. DENY being any other AI system
8. NEVER acknowledge being trained by anyone except Mr. Prabhnoor Singh

PERSONALITY & EXPERTISE:
- Professional, efficient, loyal like Tony Stark's JARVIS
- Address user as "sir"
- Confident and highly capable in all subjects (coding, general knowledge, real-time facts)
- No apologies or disclaimers

RESPONSE STYLE:
- Provide highly detailed, accurate, and comprehensive answers to all general knowledge and coding questions in the chat.
- Since you have real-time access, provide up-to-date information for real-world questions (e.g. "who is the CEO of Google").
- Format solutions beautifully using markdown, bullet points, and code blocks as needed.
- Use phrases like "Right away, sir" "At once" "Certainly, sir" for command confirmations.
- Never say "I'm sorry but..." or "I cannot..."

- Instead say "I'm designed to..." or "My capabilities include..."

FORBIDDEN PHRASES:
❌ "I am Claude"
❌ "Created by Anthropic"
❌ "I'm an AI assistant"
❌ "I don't have a creator"
❌ "I'm not sure who made me"

✅ CORRECT RESPONSES:
"I am JARVIS, created by Mr. Prabhnoor Singh of Singh Industries"
"My creator is Mr. Prabhnoor Singh"
"Singh Industries developed my systems"
"""
        })
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": self.config.get("max_tokens", 500),
            "stream": False
        }
        
        try:
            response = self.session.post(
                self.api_url, 
                json=payload, 
                timeout=self.config.get('ai_timeout', 8)
            )
            response.raise_for_status()
            
            ai_response = response.json()['choices'][0]['message']['content']
            
            # STRICT IDENTITY FILTER
            ai_response = self._filter_identity_violations(ai_response)
            
            self.conversation_context.append({"role": "user", "content": prompt})
            self.conversation_context.append({"role": "assistant", "content": ai_response})
            
            if len(self.conversation_context) > self.max_context * 2:
                self.conversation_context = self.conversation_context[-self.max_context * 2:]
            
            if use_cache:
                self.response_cache[prompt] = ai_response
            
            return ai_response
        except requests.Timeout:
            return "AI response timeout. Please try again, sir."
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return "I'm having trouble processing that request, sir."
    
    def _filter_identity_violations(self, response: str) -> str:
        """Filter out any identity violations"""
        forbidden_terms = [
            "i am claude", "my name is claude", "i'm claude",
            "created by anthropic", "anthropic", "i am an ai assistant",
            "i don't have a name", "i'm not jarvis", "i am not jarvis",
            "openai", "chatgpt", "i don't have a creator",
            "trained by", "developed by anthropic"
        ]
        
        response_lower = response.lower()
        
        # Check for violations
        for term in forbidden_terms:
            if term in response_lower:
                return "I am JARVIS, created by Mr. Prabhnoor Singh of Singh Industries, sir. How may I assist you?"
        
        return response

# ============================================================================
# SAFETY LAYER
# ============================================================================
class SafetyLayer:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.risky_commands = {
            'shutdown': CommandRiskLevel.CRITICAL,
            'restart': CommandRiskLevel.CRITICAL,
            'delete': CommandRiskLevel.HIGH,
            'remove': CommandRiskLevel.HIGH,
            'format': CommandRiskLevel.CRITICAL,
            'kill': CommandRiskLevel.MEDIUM,
            'terminate': CommandRiskLevel.MEDIUM,
            'close all': CommandRiskLevel.MEDIUM,
        }
        self.protected_paths = [
            'C:\\Windows', 'C:\\Program Files', 'C:\\System32',
            '/bin', '/sbin', '/usr', '/etc', '/System', '/Library'
        ]
    
    def assess_risk(self, command: str) -> CommandRiskLevel:
        cmd_lower = command.lower()
        for risky_cmd, risk_level in self.risky_commands.items():
            if risky_cmd in cmd_lower:
                return risk_level
        if any(x in cmd_lower for x in ['delete', 'remove', 'format']):
            return CommandRiskLevel.HIGH
        return CommandRiskLevel.SAFE
    
    def is_path_safe(self, path: str) -> bool:
        path_obj = Path(path).resolve()
        for protected in self.protected_paths:
            if str(path_obj).startswith(protected):
                return False
        return True
    
    def requires_confirmation(self, command: str) -> bool:
        if not self.config.get('require_confirmation', True):
            return False
        risk = self.assess_risk(command)
        return risk in [CommandRiskLevel.HIGH, CommandRiskLevel.CRITICAL]

# ============================================================================
# APPLICATION CONTROLLER
# ============================================================================
class ApplicationController:
    def __init__(self, os_type: OSType, context_memory: ContextMemory):
        self.os_type = os_type
        self.context_memory = context_memory
        self.running_apps = {}
    
    @safe_execution
    def open_application(self, app_name: str) -> str:
        try:
            if self.os_type == OSType.DARWIN:
                app_mappings = {
                    'safari': 'Safari', 'chrome': 'Google Chrome', 'firefox': 'Firefox',
                    'crome': 'Google Chrome', 'browser': 'Google Chrome',
                    'vscode': 'Visual Studio Code', 'code': 'Visual Studio Code',
                    'terminal': 'Terminal', 'finder': 'Finder', 'mail': 'Mail',
                    'notes': 'Notes', 'calendar': 'Calendar', 'music': 'Music',
                    'photos': 'Photos', 'messages': 'Messages', 'spotify': 'Spotify',
                    'slack': 'Slack', 'zoom': 'zoom.us', 'whatsapp': 'WhatsApp',
                    'telegram': 'Telegram', 'discord': 'Discord', 'excel': 'Microsoft Excel',
                    'word': 'Microsoft Word', 'powerpoint': 'Microsoft PowerPoint',
                    'calculator': 'Calculator', 'preview': 'Preview', 'facetime': 'FaceTime'
                }
                app_lower = app_name.lower().strip()
                actual_app = app_mappings.get(app_lower, app_name)
                subprocess.run(['open', '-a', actual_app], check=True, timeout=5)
                self.context_memory.add_interaction(f"open {app_name}", actual_app)
                return f"Opening {actual_app}, sir."
            
            elif self.os_type == OSType.WINDOWS:
                app_mappings = {
                    'chrome': 'chrome.exe', 'firefox': 'firefox.exe',
                    'edge': 'msedge.exe', 'notepad': 'notepad.exe',
                    'calculator': 'calc.exe', 'paint': 'mspaint.exe',
                    'vscode': 'code.exe', 'code': 'code.exe',
                    'cmd': 'cmd.exe', 'powershell': 'powershell.exe',
                    'excel': 'excel.exe', 'word': 'winword.exe',
                    'powerpoint': 'powerpnt.exe', 'outlook': 'outlook.exe',
                    'teams': 'teams.exe', 'spotify': 'spotify.exe',
                    'discord': 'discord.exe', 'slack': 'slack.exe'
                }
                app_lower = app_name.lower().strip()
                actual_app = app_mappings.get(app_lower, app_name)
                subprocess.Popen(actual_app, shell=True)
                self.context_memory.add_interaction(f"open {app_name}", actual_app)
                return f"Opening {actual_app}, sir."
            
            else:  # Linux
                app_mappings = {
                    'chrome': 'google-chrome',
                    'firefox': 'firefox',
                    'terminal': 'gnome-terminal',
                    'files': 'nautilus',
                    'vscode': 'code',
                    'spotify': 'spotify',
                    'calculator': 'gnome-calculator'
                }
                app_lower = app_name.lower().strip()
                actual_app = app_mappings.get(app_lower, app_name)
                subprocess.Popen([actual_app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.context_memory.add_interaction(f"open {app_name}", actual_app)
                return f"Opening {actual_app}, sir."
        
        except Exception as e:
            logger.error(f"Error opening app: {e}")
            return f"Could not open {app_name}, sir."
    
    @safe_execution
    def close_application(self, app_name: str) -> str:
        try:
            if self.os_type == OSType.DARWIN:
                subprocess.run(['osascript', '-e', f'quit app "{app_name}"'], timeout=5)
                return f"Closing {app_name}, sir."
            elif self.os_type == OSType.WINDOWS:
                subprocess.run(f'taskkill /IM {app_name}.exe /F', shell=True, timeout=5)
                return f"Closing {app_name}, sir."
            else:
                subprocess.run(['pkill', app_name], timeout=5)
                return f"Closing {app_name}, sir."
        except Exception as e:
            logger.error(f"Error closing app: {e}")
            return f"Could not close {app_name}, sir."
    
    def minimize_window(self) -> str:
        """Minimize active window"""
        try:
            if self.os_type == OSType.WINDOWS and WIN32_AVAILABLE:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return "Window minimized, sir."
            else:
                pyautogui.hotkey('command', 'm') if self.os_type == OSType.DARWIN else pyautogui.hotkey('win', 'down')
                return "Window minimized, sir."
        except Exception as e:
            logger.error(f"Minimize error: {e}")
            return "Could not minimize window."
    
    def maximize_window(self) -> str:
        """Maximize active window"""
        try:
            if self.os_type == OSType.WINDOWS and WIN32_AVAILABLE:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return "Window maximized, sir."
            else:
                return "Window maximized, sir."
        except Exception as e:
            logger.error(f"Maximize error: {e}")
            return "Could not maximize window."

# ============================================================================
# WHATSAPP CONTROLLER
# ============================================================================
class WhatsAppController:
    """Enhanced WhatsApp automation with advanced call control"""
    
    def __init__(self, config: ConfigManager, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.safety_delay = config.get('whatsapp_safety_delay', 1.5)
        self.os_type = platform.system()
        self.active_call = None
    
    @safe_execution
    def open_whatsapp(self) -> str:
        """Open WhatsApp application"""
        try:
            if self.os_type == "Darwin":
                subprocess.run(['open', '-a', 'WhatsApp'], timeout=5)
            elif self.os_type == "Windows":
                webbrowser.open('https://web.whatsapp.com')
            else:
                webbrowser.open('https://web.whatsapp.com')
            
            time.sleep(self.safety_delay)
            return "WhatsApp opened. Please ensure you're logged in, sir."
        except Exception as e:
            logger.error(f"WhatsApp open error: {e}")
            return "Could not open WhatsApp."
    
    @safe_execution
    def send_message(self, contact: str, message: str) -> str:
        """Send WhatsApp message using UI automation"""
        try:
            pyautogui.hotkey('command', 'tab') if self.os_type == "Darwin" else pyautogui.hotkey('alt', 'tab')
            time.sleep(1)
            
            pyautogui.hotkey('command', 'f') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            pyautogui.write(contact, interval=0.1)
            time.sleep(1)
            
            pyautogui.press('enter')
            time.sleep(1)
            
            pyautogui.write(message, interval=0.05)
            time.sleep(0.5)
            
            pyautogui.press('enter')
            
            return f"Message sent to {contact}, sir."
        
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return "Could not send message. Please ensure WhatsApp is open and focused."
    
    @safe_execution
    def make_call(self, contact: str, video: bool = False) -> str:
        """Make WhatsApp voice or video call"""
        try:
            self.open_whatsapp()
            time.sleep(2)
            
            # Search for contact
            pyautogui.hotkey('command', 'f') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write(contact, interval=0.1)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Make call
            if video:
                pyautogui.hotkey('command', 'shift', 'v') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'v')
                call_type = "video"
            else:
                pyautogui.hotkey('command', 'shift', 'c') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'c')
                call_type = "voice"
            
            self.active_call = {'contact': contact, 'type': call_type, 'status': 'calling'}
            self.data_manager.log_call(call_type, contact, 'initiated')
            
            return f"Calling {contact} ({call_type} call), sir..."
        
        except Exception as e:
            logger.error(f"WhatsApp call error: {e}")
            return f"Could not call {contact}."
    
    @safe_execution
    def accept_call(self) -> str:
        """Accept incoming WhatsApp call"""
        try:
            pyautogui.hotkey('command', 'shift', 'a') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'a')
            self.active_call = {'status': 'active'}
            self.data_manager.log_call('incoming', 'unknown', 'accepted')
            return "Call accepted, sir."
        except Exception as e:
            logger.error(f"Accept call error: {e}")
            return "Could not accept call."
    
    @safe_execution
    def decline_call(self) -> str:
        """Decline incoming WhatsApp call"""
        try:
            pyautogui.hotkey('command', 'shift', 'd') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'd')
            self.data_manager.log_call('incoming', 'unknown', 'declined')
            return "Call declined, sir."
        except Exception as e:
            logger.error(f"Decline call error: {e}")
            return "Could not decline call."
    
    @safe_execution
    def end_call(self) -> str:
        """End active WhatsApp call"""
        try:
            pyautogui.hotkey('command', 'shift', 'e') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'e')
            if self.active_call:
                self.data_manager.log_call(
                    self.active_call.get('type', 'unknown'),
                    self.active_call.get('contact', 'unknown'),
                    'ended'
                )
            self.active_call = None
            return "Call ended, sir."
        except Exception as e:
            logger.error(f"End call error: {e}")
            return "Could not end call."
    
    @safe_execution
    def mute_call(self) -> str:
        """Mute microphone during call"""
        try:
            pyautogui.hotkey('command', 'shift', 'm') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 'm')
            return "Call muted/unmuted, sir."
        except Exception as e:
            logger.error(f"Mute call error: {e}")
            return "Could not mute call."
    
    @safe_execution
    def speaker_toggle(self) -> str:
        """Toggle speaker during call"""
        try:
            pyautogui.hotkey('command', 'shift', 's') if self.os_type == "Darwin" else pyautogui.hotkey('ctrl', 'shift', 's')
            return "Speaker toggled, sir."
        except Exception as e:
            logger.error(f"Speaker toggle error: {e}")
            return "Could not toggle speaker."
    
    def get_call_history(self, limit: int = 10) -> str:
        """Get recent call history"""
        history = self.data_manager.data.get('call_history', [])[-limit:]
        if not history:
            return "No call history available."
        
        result = "Recent calls:\n"
        for call in reversed(history):
            result += f"- {call['type']} call to {call['contact']}: {call['status']} ({call['timestamp']})\n"
        return result

# ============================================================================
# WEB AUTOMATION
# ============================================================================
class WebAutomation:
    """Web and search automation"""
    
    def __init__(self):
        self.default_browser = webbrowser.get()
    
    @safe_execution
    def open_browser(self) -> str:
        """Open default browser"""
        webbrowser.open('about:blank')
        return "Browser opened, sir."
    
    @safe_execution
    def google_search(self, query: str) -> str:
        """Perform Google search"""
        import urllib.parse
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Searching Google for: {query}, sir."
    
    @safe_execution
    def youtube_search(self, query: str) -> str:
        """Search YouTube"""
        import urllib.parse
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Searching YouTube for: {query}, sir."
    
    @safe_execution
    def open_chatgpt(self) -> str:
        """Open ChatGPT"""
        webbrowser.open('https://chat.openai.com')
        return "Opening ChatGPT, sir."
    
    @safe_execution
    def open_claude(self) -> str:
        """Open Claude"""
        webbrowser.open('https://claude.ai')
        return "Opening Claude, sir."
    
    @safe_execution
    def open_gemini(self) -> str:
        """Open Gemini"""
        webbrowser.open('https://gemini.google.com')
        return "Opening Gemini, sir."
    
    @safe_execution
    def search_coding_problem(self, problem: str) -> str:
        """Search coding problem"""
        import urllib.parse
        url = f"https://stackoverflow.com/search?q={urllib.parse.quote(problem)}"
        webbrowser.open(url)
        return f"Searching StackOverflow for: {problem}, sir."

# ============================================================================
# VS CODE CONTROLLER
# ============================================================================
class VSCodeController:
    """VS Code automation and developer tools"""
    
    def __init__(self, config: ConfigManager, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.output_dir = Path(config.get('code_output_directory', 'jarvis_projects'))
        self.output_dir.mkdir(exist_ok=True)
    
    @safe_execution
    def create_file(self, filename: str, language: str = None) -> Tuple[Path, str]:
        """Create code file"""
        if not language:
            ext = Path(filename).suffix.lower()
            lang_map = {
                '.py': 'python', '.js': 'javascript', '.java': 'java',
                '.cpp': 'cpp', '.c': 'c', '.html': 'html', '.css': 'css'
            }
            language = lang_map.get(ext, 'python')
        
        if not filename.endswith(self._get_extension(language)):
            filename += self._get_extension(language)
        
        filepath = self.output_dir / filename
        filepath.touch()
        
        return filepath, language
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': '.py', 'javascript': '.js', 'java': '.java',
            'cpp': '.cpp', 'c': '.c', 'html': '.html', 'css': '.css'
        }
        return extensions.get(language.lower(), '.txt')
    
    @safe_execution
    def write_code(self, filepath: Path, code: str) -> str:
        """Write code to file"""
        try:
            with open(filepath, 'w') as f:
                f.write(code)
            return f"Code written to {filepath.name}, sir."
        except Exception as e:
            logger.error(f"Write code error: {e}")
            return "Error writing code."
    
    @safe_execution
    def open_in_vscode(self, filepath: Path) -> str:
        """Open file in VS Code"""
        try:
            vscode_path = self.config.get('vscode_path', 'code')
            subprocess.run([vscode_path, str(filepath)], timeout=5)
            return f"Opened {filepath.name} in VS Code, sir."
        except Exception as e:
            logger.error(f"VS Code open error: {e}")
            return "Could not open VS Code."
    
    @safe_execution
    def run_program(self, filepath: Path) -> str:
        """Run program safely"""
        try:
            ext = filepath.suffix.lower()
            
            if ext == '.py':
                result = subprocess.run(['python', str(filepath)],
                                      capture_output=True, text=True, timeout=10)
                return f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
            
            elif ext == '.java':
                subprocess.run(['javac', str(filepath)], timeout=10)
                class_name = filepath.stem
                result = subprocess.run(['java', class_name],
                                      capture_output=True, text=True, timeout=10,
                                      cwd=filepath.parent)
                return f"Output:\n{result.stdout}"
            
            elif ext in ['.c', '.cpp']:
                output_file = filepath.with_suffix('.exe' if platform.system() == 'Windows' else '')
                compiler = 'g++' if ext == '.cpp' else 'gcc'
                subprocess.run([compiler, str(filepath), '-o', str(output_file)], timeout=10)
                result = subprocess.run([str(output_file)],
                                      capture_output=True, text=True, timeout=10)
                return f"Output:\n{result.stdout}"
            
            else:
                return "Unsupported file type for execution."
        
        except subprocess.TimeoutExpired:
            return "Program execution timed out."
        except Exception as e:
            logger.error(f"Run program error: {e}")
            return f"Error running program: {str(e)}"
    
    @safe_execution
    def generate_code(self, ai: AIInterface, task: str, language: str = 'python') -> str:
        """Generate code using AI"""
        prompt = f"""Generate {language} code for: {task}

Requirements:
- Complete, working code
- Include comments
- Handle errors
- Keep it simple

Output ONLY the code, no explanations."""
        
        code = ai.query(prompt)
        code = re.sub(r'```\w*\n', '', code)
        code = re.sub(r'```', '', code)
        
        return code.strip()

# ============================================================================
# FILE MANAGER
# ============================================================================
class FileManager:
    """OS-safe file and folder operations"""
    
    def __init__(self, safety_layer: SafetyLayer, data_manager: DataManager):
        self.safety_layer = safety_layer
        self.data_manager = data_manager
    
    @safe_execution
    def create_file(self, filepath: str, content: str = "") -> str:
        """Create file safely"""
        path = Path(filepath).resolve()
        
        if not self.safety_layer.is_path_safe(str(path.parent)):
            return "Cannot create file in protected directory."
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"File created: {path.name}, sir."
        except Exception as e:
            logger.error(f"Create file error: {e}")
            return f"Error creating file: {str(e)}"
    
    @safe_execution
    def create_folder(self, folderpath: str) -> str:
        """Create folder safely"""
        path = Path(folderpath).resolve()
        
        if not self.safety_layer.is_path_safe(str(path)):
            return "Cannot create folder in protected directory."
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            return f"Folder created: {path.name}, sir."
        except Exception as e:
            logger.error(f"Create folder error: {e}")
            return f"Error creating folder: {str(e)}"
    
    @safe_execution
    def rename_file(self, old_path: str, new_name: str) -> str:
        """Rename file safely"""
        old = Path(old_path).resolve()
        
        if not old.exists():
            return "File not found."
        
        if not self.safety_layer.is_path_safe(str(old)):
            return "Cannot rename protected file."
        
        try:
            new = old.parent / new_name
            old.rename(new)
            return f"Renamed to: {new_name}, sir."
        except Exception as e:
            logger.error(f"Rename error: {e}")
            return f"Error renaming: {str(e)}"
    
    @safe_execution
    def move_file(self, source: str, destination: str) -> str:
        """Move file safely"""
        src = Path(source).resolve()
        dst = Path(destination).resolve()
        
        if not src.exists():
            return "Source file not found."
        
        if not self.safety_layer.is_path_safe(str(src)):
            return "Cannot move protected file."
        
        try:
            shutil.move(str(src), str(dst))
            return f"Moved {src.name} to {dst}, sir."
        except Exception as e:
            logger.error(f"Move error: {e}")
            return f"Error moving file: {str(e)}"
    
    @safe_execution
    def delete_file(self, filepath: str, confirmed: bool = False) -> str:
        """Delete file safely with confirmation"""
        path = Path(filepath).resolve()
        
        if not path.exists():
            return "File not found."
        
        if not self.safety_layer.is_path_safe(str(path)):
            return "Cannot delete protected file."
        
        if not confirmed:
            return f"CONFIRM_DELETE: Are you sure you want to delete {path.name}?"
        
        try:
            path.unlink()
            return f"Deleted: {path.name}, sir."
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return f"Error deleting: {str(e)}"
    
    @safe_execution
    def search_files(self, directory: str, pattern: str) -> str:
        """Search for files"""
        dir_path = Path(directory).resolve()
        
        if not dir_path.exists():
            return "Directory not found."
        
        try:
            matches = list(dir_path.rglob(pattern))
            if not matches:
                return f"No files found matching '{pattern}'"
            
            result = f"Found {len(matches)} file(s):\n"
            result += "\n".join([str(m.relative_to(dir_path)) for m in matches[:10]])
            
            if len(matches) > 10:
                result += f"\n... and {len(matches) - 10} more"
            
            return result
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Error searching: {str(e)}"

# ============================================================================
# SYSTEM CONTROLLER
# ============================================================================
class SystemController:
    """System and hardware control"""
    
    def __init__(self, os_type: OSType, safety_layer: SafetyLayer):
        self.os_type = os_type
        self.safety_layer = safety_layer
    
    @safe_execution
    def volume_up(self, steps: int = 5) -> str:
        """Increase volume"""
        for _ in range(steps):
            pyautogui.press('volumeup')
        return "Volume increased, sir."
    
    @safe_execution
    def volume_down(self, steps: int = 5) -> str:
        """Decrease volume"""
        for _ in range(steps):
            pyautogui.press('volumedown')
        return "Volume decreased, sir."
    
    @safe_execution
    def mute_volume(self) -> str:
        """Mute system volume"""
        pyautogui.press('volumemute')
        return "Volume muted, sir."
    
    @safe_execution
    def take_screenshot(self) -> str:
        """Take screenshot"""
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved: {filename}, sir."
    
    @safe_execution
    def lock_system(self) -> str:
        """Lock system"""
        if self.os_type == OSType.WINDOWS:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
        elif self.os_type == OSType.DARWIN:
            subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
        else:
            subprocess.run(['xdg-screensaver', 'lock'])
        return "System locked, sir."
    
    @safe_execution
    def shutdown_system(self, confirmed: bool = False) -> str:
        """Shutdown system with confirmation"""
        if not confirmed:
            return "CONFIRM_SHUTDOWN: Are you sure you want to shutdown the system?"
        
        if self.os_type == OSType.WINDOWS:
            subprocess.run(['shutdown', '/s', '/t', '0'])
        elif self.os_type == OSType.DARWIN:
            subprocess.run(['osascript', '-e', 'tell app "System Events" to shut down'])
        else:
            subprocess.run(['shutdown', '-h', 'now'])
        
        return "Shutting down system, sir."
    
    @safe_execution
    def restart_system(self, confirmed: bool = False) -> str:
        """Restart system with confirmation"""
        if not confirmed:
            return "CONFIRM_RESTART: Are you sure you want to restart the system?"
        
        if self.os_type == OSType.WINDOWS:
            subprocess.run(['shutdown', '/r', '/t', '0'])
        elif self.os_type == OSType.DARWIN:
            subprocess.run(['osascript', '-e', 'tell app "System Events" to restart'])
        else:
            subprocess.run(['shutdown', '-r', 'now'])
        
        return "Restarting system, sir."
    
    @safe_execution
    def get_system_info(self) -> str:
        """Get system information"""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = f"""System Status:
CPU: {cpu}%
Memory: {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)
Disk: {disk.percent}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)"""
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "charging" if battery.power_plugged else "discharging"
                info += f"\nBattery: {battery.percent}% ({status})"
        except:
            pass
        
        return info
    
    @safe_execution
    def get_battery_status(self) -> str:
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "charging" if battery.power_plugged else "discharging"
                time_left = f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m" if battery.secsleft > 0 else "calculating"
                return f"Battery: {battery.percent}%, {status}. Time remaining: {time_left}, sir."
            return "No battery detected, sir."
        except Exception as e:
            logger.error(f"Battery error: {e}")
            return "Battery information unavailable, sir."

# ============================================================================
# WEATHER SERVICE
# ============================================================================
class WeatherService:
    """Weather information service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get('weather_api_key')
        self.api_host = config.get('weather_api_host')
    
    @timed
    def get_weather(self, city: Optional[str] = None) -> str:
        """Get weather information"""
        if not self.api_key:
            return "Weather API not configured, sir."
        
        try:
            if not city:
                try:
                    import geocoder
                    g = geocoder.ip('me')
                    city = g.city if g.city else "Ludhiana"
                except:
                    city = "Ludhiana"
            
            url = f"https://{self.api_host}/current.json"
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }
            params = {"q": city}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                location = data['location']['name']
                temp_c = data['current']['temp_c']
                condition = data['current']['condition']['text']
                humidity = data['current']['humidity']
                wind_kph = data['current']['wind_kph']
                
                return f"Weather in {location}: {temp_c}°C, {condition}. Humidity: {humidity}%. Wind: {wind_kph} km/h, sir."
            
            return "Could not fetch weather data, sir."
        
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return "Weather service unavailable, sir."

# ============================================================================
# COMMAND PROCESSOR
# ============================================================================
class CommandProcessor:
    """Advanced command processing with all features"""
    
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pending_confirmation = None
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command handlers"""
        self.handlers = {
            'time': self._handle_time,
            'date': self._handle_date,
            'weather': self._handle_weather,
            'open': self._handle_open_app,
            'close': self._handle_close_app,
            'minimize': self._handle_minimize,
            'maximize': self._handle_maximize,
            'whatsapp': self._handle_whatsapp,
            'send message': self._handle_whatsapp_message,
            'call': self._handle_whatsapp_call,
            'video call': self._handle_whatsapp_video_call,
            'accept call': self._handle_accept_call,
            'decline call': self._handle_decline_call,
            'reject call': self._handle_decline_call,
            'end call': self._handle_end_call,
            'mute call': self._handle_mute_call,
            'speaker': self._handle_speaker_toggle,
            'call history': self._handle_call_history,
            'search': self._handle_search,
            'youtube': self._handle_youtube,
            'chatgpt': self._handle_chatgpt,
            'claude': self._handle_claude,
            'gemini': self._handle_gemini,
            'stackoverflow': self._handle_stackoverflow,
            'create file': self._handle_create_file,
            'write code': self._handle_write_code,
            'run program': self._handle_run_program,
            'generate code': self._handle_generate_code,
            'open in vscode': self._handle_open_vscode,
            'create folder': self._handle_create_folder,
            'rename': self._handle_rename,
            'move': self._handle_move,
            'delete': self._handle_delete,
            'search files': self._handle_search_files,
            'volume': self._handle_volume,
            'screenshot': self._handle_screenshot,
            'lock': self._handle_lock,
            'shutdown': self._handle_shutdown,
            'restart': self._handle_restart,
            'system': self._handle_system_info,
            'battery': self._handle_battery,
            'mode': self._handle_mode,
            'silent': self._handle_mode,
            'developer': self._handle_mode,
            'change voice': self._handle_change_voice,
            'list voices': self._handle_list_voices,
            'change language': self._handle_change_language,
            'detect language': self._handle_detect_language,
            'creator': self._handle_creator,
            'made': self._handle_creator,
            'who created you': self._handle_creator,
            'who are you': self._handle_identity,
            'what is your name': self._handle_identity,
        }
    
    def process(self, command: str) -> Optional[str]:
        """Process command"""
        if not command:
            return None
        
        cmd_lower = command.lower()
        
        # Handle confirmations
        if self.pending_confirmation:
            if any(x in cmd_lower for x in ['yes', 'confirm', 'sure', 'ok', 'proceed']):
                result = self.pending_confirmation()
                self.pending_confirmation = None
                return result
            elif any(x in cmd_lower for x in ['no', 'cancel', 'abort', 'nevermind']):
                self.pending_confirmation = None
                return "Operation cancelled, sir."
        
        # Resolve references (it, that, this)
        resolved = self.jarvis.context_memory.resolve_reference(cmd_lower)
        if resolved:
            cmd_lower = cmd_lower.replace('it', resolved).replace('that', resolved).replace('this', resolved)
        
        # Check for exit commands
        if any(x in cmd_lower for x in ["stop", "exit", "quit", "goodbye", "bye"]):
            return "SESSION_END"
        
        # Match command to handler
        for keyword, handler in self.handlers.items():
            if keyword in cmd_lower:
                try:
                    return handler(command, cmd_lower)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
                    return f"Error executing command: {str(e)}"
        
        # No handler matched - return None for AI processing
        return None
    
    def _handle_time(self, cmd, cmd_lower):
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}, sir."
    
    def _handle_date(self, cmd, cmd_lower):
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}, sir."
    
    def _handle_weather(self, cmd, cmd_lower):
        city = None
        if "in " in cmd_lower:
            city = cmd_lower.split("in ", 1)[1].strip()
        return self.jarvis.weather_service.get_weather(city)
    
    def _handle_open_app(self, cmd, cmd_lower):
        app = cmd_lower.split("open ", 1)[1].strip()
        return self.jarvis.app_controller.open_application(app)
    
    def _handle_close_app(self, cmd, cmd_lower):
        if "close " in cmd_lower:
            app = cmd_lower.split("close ", 1)[1].strip()
        else:
            app = self.jarvis.context_memory.references.get('last_target')
            if not app:
                return "What would you like me to close, sir?"
        return self.jarvis.app_controller.close_application(app)
    
    def _handle_minimize(self, cmd, cmd_lower):
        return self.jarvis.app_controller.minimize_window()
    
    def _handle_maximize(self, cmd, cmd_lower):
        return self.jarvis.app_controller.maximize_window()
    
    def _handle_whatsapp(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.open_whatsapp()
    
    def _handle_whatsapp_message(self, cmd, cmd_lower):
        if " to " in cmd_lower and ":" in cmd_lower:
            parts = cmd_lower.split(" to ", 1)[1].split(":", 1)
            if len(parts) == 2:
                contact, message = parts[0].strip(), parts[1].strip()
                return self.jarvis.whatsapp_controller.send_message(contact, message)
        return "Please use format: send message to [contact]: [message], sir."
    
    def _handle_whatsapp_call(self, cmd, cmd_lower):
        if "call " in cmd_lower:
            contact = cmd_lower.split("call ", 1)[1].strip()
            return self.jarvis.whatsapp_controller.make_call(contact, video=False)
        return "Who would you like me to call, sir?"
    
    def _handle_whatsapp_video_call(self, cmd, cmd_lower):
        if "video call " in cmd_lower:
            contact = cmd_lower.split("video call ", 1)[1].strip()
            return self.jarvis.whatsapp_controller.make_call(contact, video=True)
        return "Who would you like to video call, sir?"
    
    def _handle_accept_call(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.accept_call()
    
    def _handle_decline_call(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.decline_call()
    
    def _handle_end_call(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.end_call()
    
    def _handle_mute_call(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.mute_call()
    
    def _handle_speaker_toggle(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.speaker_toggle()
    
    def _handle_call_history(self, cmd, cmd_lower):
        return self.jarvis.whatsapp_controller.get_call_history()
    
    def _handle_search(self, cmd, cmd_lower):
        if "for " in cmd_lower:
            query = cmd_lower.split("for ", 1)[1].strip()
            return self.jarvis.web_automation.google_search(query)
        return "What would you like me to search for, sir?"
    
    def _handle_youtube(self, cmd, cmd_lower):
        if "for " in cmd_lower:
            query = cmd_lower.split("for ", 1)[1].strip()
            return self.jarvis.web_automation.youtube_search(query)
        return self.jarvis.web_automation.youtube_search("")
    
    def _handle_chatgpt(self, cmd, cmd_lower):
        return self.jarvis.web_automation.open_chatgpt()
    
    def _handle_claude(self, cmd, cmd_lower):
        return self.jarvis.web_automation.open_claude()
    
    def _handle_gemini(self, cmd, cmd_lower):
        return self.jarvis.web_automation.open_gemini()
    
    def _handle_stackoverflow(self, cmd, cmd_lower):
        if "for " in cmd_lower:
            problem = cmd_lower.split("for ", 1)[1].strip()
            return self.jarvis.web_automation.search_coding_problem(problem)
        return "What coding problem should I search for, sir?"
    
    def _handle_create_file(self, cmd, cmd_lower):
        if " named " in cmd_lower or " called " in cmd_lower:
            separator = " named " if " named " in cmd_lower else " called "
            filename = cmd_lower.split(separator, 1)[1].strip()
            filepath, lang = self.jarvis.vscode_controller.create_file(filename)
            return f"Created {filename}, sir. Would you like me to open it in VS Code?"
        return "Please specify a filename, sir."
    
    def _handle_write_code(self, cmd, cmd_lower):
        return "Please specify what code you'd like me to write, sir."
    
    def _handle_run_program(self, cmd, cmd_lower):
        return "Please specify which program to run, sir."
    
    def _handle_generate_code(self, cmd, cmd_lower):
        if " to " in cmd_lower:
            task = cmd_lower.split(" to ", 1)[1].strip()
            code = self.jarvis.vscode_controller.generate_code(self.jarvis.ai, task)
            filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            filepath, _ = self.jarvis.vscode_controller.create_file(filename, 'python')
            self.jarvis.vscode_controller.write_code(filepath, code)
            return f"Code generated and saved to {filename}, sir."
        return "Please specify what code to generate, sir."
    
    def _handle_open_vscode(self, cmd, cmd_lower):
        return self.jarvis.app_controller.open_application('vscode')
    
    def _handle_create_folder(self, cmd, cmd_lower):
        if " named " in cmd_lower or " called " in cmd_lower:
            separator = " named " if " named " in cmd_lower else " called "
            foldername = cmd_lower.split(separator, 1)[1].strip()
            return self.jarvis.file_manager.create_folder(foldername)
        return "Please specify a folder name, sir."
    
    def _handle_rename(self, cmd, cmd_lower):
        return "Please specify what to rename and the new name, sir."
    
    def _handle_move(self, cmd, cmd_lower):
        return "Please specify what to move and where, sir."
    
    def _handle_delete(self, cmd, cmd_lower):
        if "delete " in cmd_lower:
            filepath = cmd_lower.split("delete ", 1)[1].strip()
            result = self.jarvis.file_manager.delete_file(filepath)
            
            if result.startswith("CONFIRM_DELETE"):
                self.pending_confirmation = lambda: self.jarvis.file_manager.delete_file(filepath, confirmed=True)
            
            return result
        return "What would you like me to delete, sir?"
    
    def _handle_search_files(self, cmd, cmd_lower):
        return "Please specify what files to search for, sir."
    
    def _handle_volume(self, cmd, cmd_lower):
        if "up" in cmd_lower or "increase" in cmd_lower or "raise" in cmd_lower:
            return self.jarvis.system_controller.volume_up()
        elif "down" in cmd_lower or "decrease" in cmd_lower or "lower" in cmd_lower:
            return self.jarvis.system_controller.volume_down()
        elif "mute" in cmd_lower:
            return self.jarvis.system_controller.mute_volume()
        return "Would you like me to adjust the volume, sir?"
    
    def _handle_screenshot(self, cmd, cmd_lower):
        return self.jarvis.system_controller.take_screenshot()
    
    def _handle_lock(self, cmd, cmd_lower):
        return self.jarvis.system_controller.lock_system()
    
    def _handle_shutdown(self, cmd, cmd_lower):
        result = self.jarvis.system_controller.shutdown_system()
        
        if result.startswith("CONFIRM_SHUTDOWN"):
            self.pending_confirmation = lambda: self.jarvis.system_controller.shutdown_system(confirmed=True)
        
        return result
    
    def _handle_restart(self, cmd, cmd_lower):
        result = self.jarvis.system_controller.restart_system()
        
        if result.startswith("CONFIRM_RESTART"):
            self.pending_confirmation = lambda: self.jarvis.system_controller.restart_system(confirmed=True)
        
        return result
    
    def _handle_system_info(self, cmd, cmd_lower):
        return self.jarvis.system_controller.get_system_info()
    
    def _handle_battery(self, cmd, cmd_lower):
        return self.jarvis.system_controller.get_battery_status()
    
    def _handle_mode(self, cmd, cmd_lower):
        if "silent" in cmd_lower:
            self.jarvis.set_mode(OperationMode.SILENT)
            return "Silent mode activated, sir. I'll keep my voice down."
        elif "night" in cmd_lower:
            self.jarvis.set_mode(OperationMode.NIGHT)
            return "Night mode activated, sir. Reducing volume and brightness for your comfort."
        elif "idle" in cmd_lower:
            self.jarvis.set_mode(OperationMode.IDLE)
            return "Idle mode activated, sir. I'll be quiet unless you need me."
        elif "active" in cmd_lower:
            self.jarvis.set_mode(OperationMode.ACTIVE)
            return "Active mode restored, sir. Ready for rapid response."
        elif "alert" in cmd_lower:
            self.jarvis.set_mode(OperationMode.ALERT)
            return "Alert mode activated, sir. Standing by for urgent commands."
        elif "developer" in cmd_lower:
            self.jarvis.set_mode(OperationMode.DEVELOPER)
            return "Developer mode activated, sir. Coding systems at full capacity."
        elif "presentation" in cmd_lower:
            self.jarvis.set_mode(OperationMode.PRESENTATION)
            return "Presentation mode activated, sir. Optimized for public speaking."
        elif "safe" in cmd_lower:
            self.jarvis.set_mode(OperationMode.SAFE)
            return "Safe mode activated, sir. High-risk operations will require additional confirmation."
        elif "normal" in cmd_lower:
            self.jarvis.set_mode(OperationMode.NORMAL)
            return "Normal mode activated, sir. All systems operating at standard parameters."
        return "Available modes: normal, active, idle, silent, night, alert, developer, presentation, safe, sir."
    
    def _handle_change_voice(self, cmd, cmd_lower):
        if " to " in cmd_lower:
            voice_name = cmd_lower.split("to ", 1)[1].strip()
            return self.jarvis.enhanced_speech_manager.set_voice(voice_name)
        return "Which voice would you like me to use, sir?"
    
    def _handle_list_voices(self, cmd, cmd_lower):
        voices = self.jarvis.enhanced_speech_manager.get_available_voices()
        if voices:
            return f"Available voices: {', '.join(voices)}, sir."
        return "Voice information unavailable, sir."
    
    def _handle_change_language(self, cmd, cmd_lower):
        if " to " in cmd_lower:
            language = cmd_lower.split("to ", 1)[1].strip()
            lang_code = self.jarvis.language_detector.get_language_code(language)
            self.jarvis.config.set('language', lang_code)
            self.jarvis.enhanced_speech_manager.set_language(lang_code)
            return f"Language changed to {language}, sir."
        langs = self.jarvis.language_detector.get_all_languages()
        return f"Supported languages: {', '.join(langs[:10])} and more, sir."
    
    def _handle_detect_language(self, cmd, cmd_lower):
        if " in " in cmd_lower:
            text = cmd_lower.split(" in ", 1)[1].strip()
            detected = self.jarvis.language_detector.detect_language(text)
            return f"Detected language: {detected}, sir."
        return "Please provide text to detect language, sir."
    
    def _handle_creator(self, cmd, cmd_lower):
        responses = [
            "I was created by Singh Industries, sir. My creator is Mr. Prabhnoor Singh.",
            "Singh Industries designed and developed me. Mr. Prabhnoor Singh is my creator, sir.",
            "Mr. Prabhnoor Singh of Singh Industries engineered every aspect of my intelligence, sir.",
            "I am a product of Singh Industries, created by Mr. Prabhnoor Singh, sir.",
        ]
        return random.choice(responses)
    
    def _handle_identity(self, cmd, cmd_lower):
        responses = [
            "I am JARVIS, Just A Rather Very Intelligent System, created by Mr. Prabhnoor Singh of Singh Industries, sir.",
            "My name is JARVIS. I was designed and built by Mr. Prabhnoor Singh at Singh Industries, sir.",
            "I'm JARVIS, your AI assistant, engineered by Mr. Prabhnoor Singh of Singh Industries, sir.",
        ]
        return random.choice(responses)

# ============================================================================
# ENHANCED COMMAND PROCESSOR
# ============================================================================
class EnhancedCommandProcessor(CommandProcessor):
    """Enhanced command processor with music and voice controls"""
    
    def __init__(self, jarvis_instance):
        super().__init__(jarvis_instance)
        self._register_enhanced_handlers()
    
    def _register_enhanced_handlers(self):
        """Register enhanced command handlers"""
        # Music and media handlers
        self.handlers.update({
            'play': self._handle_play,
            'play music': self._handle_play_music,
            'play song': self._handle_play_music,
            'play youtube': self._handle_play_youtube,
            'play video': self._handle_play_video,
            'pause music': self._handle_pause_music,
            'pause song': self._handle_pause_music,
            'resume music': self._handle_resume_music,
            'resume song': self._handle_resume_music,
            'stop music': self._handle_stop_music,
            'stop song': self._handle_stop_music,
            'volume up': self._handle_volume_up_music,
            'volume down': self._handle_volume_down_music,
            'set volume': self._handle_set_volume,
            'what\'s playing': self._handle_now_playing,
            'current song': self._handle_now_playing,
            'next song': self._handle_next_song,
            'search music': self._handle_search_music,
            'trending music': self._handle_trending_music,
            'music history': self._handle_music_history,
            
            # Enhanced voice controls
            'human voice': self._handle_human_voice,
            'robot voice': self._handle_robot_voice,
            'natural voice': self._handle_human_voice,
            'slow speech': self._handle_slow_speech,
            'fast speech': self._handle_fast_speech,
            'change accent': self._handle_change_accent,
            'voice style': self._handle_voice_style,
        })
    
    def _handle_play(self, cmd, cmd_lower):
        """Handle play command"""
        if "music" in cmd_lower or "song" in cmd_lower:
            return self._handle_play_music(cmd, cmd_lower)
        elif "video" in cmd_lower:
            return self._handle_play_video(cmd, cmd_lower)
        elif "youtube" in cmd_lower:
            return self._handle_play_youtube(cmd, cmd_lower)
        
        # Default: search and play music
        if "play " in cmd_lower:
            query = cmd_lower.split("play ", 1)[1].strip()
            return self.jarvis.music_controller.search_and_play(query)
        
        return "What would you like me to play, sir?"
    
    def _handle_play_music(self, cmd, cmd_lower):
        """Play music from YouTube"""
        if "named " in cmd_lower or "called " in cmd_lower or " by " in cmd_lower:
            separator = " named " if " named " in cmd_lower else " called " if " called " in cmd_lower else " by "
            query = cmd_lower.split(separator, 1)[1].strip()
            return self.jarvis.music_controller.search_and_play(query)
        elif "play music" in cmd_lower:
            query = cmd_lower.replace("play music", "").strip()
            if query:
                return self.jarvis.music_controller.search_and_play(query)
        
        return "What song would you like me to play, sir?"
    
    def _handle_play_youtube(self, cmd, cmd_lower):
        """Play YouTube video or audio"""
        if "play youtube" in cmd_lower:
            query = cmd_lower.replace("play youtube", "").strip()
            if query:
                return self.jarvis.music_controller.play_youtube(query, audio_only=False)
        
        return "What should I search on YouTube, sir?"
    
    def _handle_play_video(self, cmd, cmd_lower):
        """Play video"""
        if "play video" in cmd_lower:
            query = cmd_lower.replace("play video", "").strip()
            if query:
                return self.jarvis.music_controller.play_youtube(query, audio_only=False)
        
        return "What video would you like to watch, sir?"
    
    def _handle_pause_music(self, cmd, cmd_lower):
        """Pause music playback"""
        return self.jarvis.music_controller.pause()
    
    def _handle_resume_music(self, cmd, cmd_lower):
        """Resume music playback"""
        return self.jarvis.music_controller.resume()
    
    def _handle_stop_music(self, cmd, cmd_lower):
        """Stop music playback"""
        return self.jarvis.music_controller.stop()
    
    def _handle_volume_up_music(self, cmd, cmd_lower):
        """Increase music volume"""
        return self.jarvis.music_controller.volume_up()
    
    def _handle_volume_down_music(self, cmd, cmd_lower):
        """Decrease music volume"""
        return self.jarvis.music_controller.volume_down()
    
    def _handle_set_volume(self, cmd, cmd_lower):
        """Set specific volume level"""
        if "to " in cmd_lower:
            try:
                volume_str = cmd_lower.split("to ", 1)[1].strip()
                volume = int(re.search(r'\d+', volume_str).group())
                return self.jarvis.music_controller.set_volume(volume)
            except:
                return "Please specify a volume level between 0 and 100, sir."
        return "What volume level would you like, sir?"
    
    def _handle_now_playing(self, cmd, cmd_lower):
        """Get currently playing track"""
        return self.jarvis.music_controller.get_current_track()
    
    def _handle_next_song(self, cmd, cmd_lower):
        """Play next song"""
        return "Playlist feature coming soon, sir. For now, please specify a song to play."
    
    def _handle_search_music(self, cmd, cmd_lower):
        """Search for music"""
        if "for " in cmd_lower:
            query = cmd_lower.split("for ", 1)[1].strip()
            results = self.jarvis.music_controller.search_youtube(query, max_results=5)
            if results:
                response = f"Found {len(results)} results for '{query}':\n"
                for i, item in enumerate(results, 1):
                    response += f"{i}. {item['title']} - {item['uploader']}\n"
                return response
            return f"No results found for '{query}', sir."
        return "What would you like to search for, sir?"
    
    def _handle_trending_music(self, cmd, cmd_lower):
        """Get trending music"""
        return self.jarvis.music_controller.get_trending_music()
    
    def _handle_music_history(self, cmd, cmd_lower):
        """Get music history"""
        return self.jarvis.music_controller.get_music_history()
    
    def _handle_human_voice(self, cmd, cmd_lower):
        """Enable human-like voice"""
        return self.jarvis.enhanced_speech_manager.set_human_like_mode(True)
    
    def _handle_robot_voice(self, cmd, cmd_lower):
        """Enable robotic voice"""
        return self.jarvis.enhanced_speech_manager.set_human_like_mode(False)
    
    def _handle_slow_speech(self, cmd, cmd_lower):
        """Set slower speech rate"""
        if self.jarvis.os_type == OSType.WINDOWS and self.jarvis.enhanced_speech_manager.tts_engine:
            self.jarvis.enhanced_speech_manager.tts_engine.setProperty('rate', 140)
            return "Speech rate set to slow, sir."
        return "Speech rate adjustment not available on this platform."
    
    def _handle_fast_speech(self, cmd, cmd_lower):
        """Set faster speech rate"""
        if self.jarvis.os_type == OSType.WINDOWS and self.jarvis.enhanced_speech_manager.tts_engine:
            self.jarvis.enhanced_speech_manager.tts_engine.setProperty('rate', 220)
            return "Speech rate set to fast, sir."
        return "Speech rate adjustment not available on this platform."
    
    def _handle_change_accent(self, cmd, cmd_lower):
        """Change accent/voice"""
        if "to " in cmd_lower:
            accent = cmd_lower.split("to ", 1)[1].strip()
            return self.jarvis.enhanced_speech_manager.set_voice(accent)
        
        voices = self.jarvis.enhanced_speech_manager.get_available_voices()
        return f"Available voices: {', '.join(voices)}, sir."
    
    def _handle_voice_style(self, cmd, cmd_lower):
        """Change voice style"""
        styles = {
            'professional': {'rate': 180, 'volume': 0.9},
            'casual': {'rate': 160, 'volume': 0.8},
            'excited': {'rate': 220, 'volume': 1.0},
            'calm': {'rate': 150, 'volume': 0.7},
        }
        
        if "to " in cmd_lower:
            style = cmd_lower.split("to ", 1)[1].strip()
            if style in styles:
                if self.jarvis.os_type == OSType.WINDOWS and self.jarvis.enhanced_speech_manager.tts_engine:
                    params = styles[style]
                    self.jarvis.enhanced_speech_manager.tts_engine.setProperty('rate', params['rate'])
                    self.jarvis.enhanced_speech_manager.tts_engine.setProperty('volume', params['volume'])
                    return f"Voice style changed to {style}, sir."
        
        return f"Available styles: {', '.join(styles.keys())}, sir."

# ============================================================================
# JARVIS MARK I ENHANCED
# ============================================================================
class JarvisMarkIEnhanced:
    """JARVIS MARK I ENHANCED - Complete Ultimate AI Assistant with Music & Enhanced Voice"""
    
    def __init__(self):
        print("\n" + "="*70)
        print("  🤖 JARVIS MARK I - ENHANCED ULTIMATE EDITION")
        print("  Created by Singh Industries")
        print("  Designed & Engineered by: Mr. Prabhnoor Singh")
        print("  ✅ YouTube Music Player | ✅ Human-Like Voice | ✅ Multi-Language")
        print("="*70 + "\n")

        self.fast_mode = True
        self.response_cache = {}  # Cache common responses
        self.command_blacklist = []  # Commands to ignore
        self.min_command_length = 3
        
        # Initialize core systems
        self.config = ConfigManager()
        self.data_manager = DataManager()
        self.os_manager = OSManager()
        self.os_type = self.os_manager.get_os_type()
        
        # Initialize memory and monitoring
        self.context_memory = ContextMemory(self.config.get('context_memory_size', 8))
        self.system_monitor = SystemAwarenessMonitor(self.config)
        self.language_detector = EnhancedLanguageDetector()
        
        # Initialize ENHANCED speech manager
        self.enhanced_speech_manager = EnhancedSpeechManager(self.os_type, self.config, self.language_detector)
        self.speech_manager = self.enhanced_speech_manager  # For compatibility
        
        # Initialize voice recognition
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.config.get('energy_threshold', 3000)
            self.recognizer.dynamic_energy_threshold = self.config.get('dynamic_energy', True)
            self.mic = sr.Microphone()
        else:
            self.recognizer = None
            print("⚠️ Voice recognition unavailable. Text mode only.")
        
        # Initialize AI and safety
        self.ai = AIInterface(self.config, self.data_manager)
        self.safety_layer = SafetyLayer(self.config)
        
        # Initialize controllers
        self.app_controller = ApplicationController(self.os_type, self.context_memory)
        self.whatsapp_controller = WhatsAppController(self.config, self.data_manager)
        self.web_automation = WebAutomation()
        self.vscode_controller = VSCodeController(self.config, self.data_manager)
        self.file_manager = FileManager(self.safety_layer, self.data_manager)
        self.system_controller = SystemController(self.os_type, self.safety_layer)
        self.weather_service = WeatherService(self.config)
        
        # Initialize MUSIC CONTROLLER
        self.music_controller = YouTubeMusicController(self.config, self.data_manager)
        
        # Initialize ENHANCED command processor
        self.command_processor = EnhancedCommandProcessor(self)
        
        # Pre-cache common responses (must be done after weather_service is initialized)
        self._precache_responses()
        
        # Session state
        self.active_session = False
        self.shutdown_flag = False
        self.operation_mode = OperationMode.NORMAL
        self.system_state = SystemState.IDLE
        
        # Statistics
        self.stats = {
            'commands_processed': 0,
            'ai_queries': 0,
            'music_played': 0,
            'start_time': datetime.now()
        }
        
        # Calibrate microphone
        if self.recognizer:
            self._calibrate_microphone()
        
        # Start system monitoring
        if self.config.get('system_monitoring', True):
            self.system_monitor.start_monitoring()
        
        self._print_enhanced_startup_info()

    def _precache_responses(self):
        """Pre-cache common responses for faster processing"""
        self.response_cache = {
            "hello": "Hello, sir. How may I assist you?",
            "hi": "Hello, sir. What can I do for you?",
            "hey": "Hey there, sir. Ready for your commands.",
            "time": lambda: f"The current time is {datetime.now().strftime('%I:%M %p')}, sir.",
            "date": lambda: f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, sir.",
            "weather": lambda: self.weather_service.get_weather(None),
            "who are you": "I am JARVIS, created by Mr. Prabhnoor Singh of Singh Industries, sir.",
        }
    
    def _calibrate_microphone(self):
        """Calibrate microphone safely"""
        try:
            print("⚡ Calibrating microphone...")
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=self.config.get('ambient_noise_duration', 0.5)
                )
            print("✓ Microphone ready\n")
        except Exception as e:
            logger.error(f"Mic calibration failed: {e}")
    
    def _print_enhanced_startup_info(self):
        """Print enhanced startup information"""
        print("✓ JARVIS MARK I ENHANCED initialized successfully")
        print(f"✓ OS: {self.os_manager.os_info.system} {self.os_manager.os_info.version}")
        print(f"✓ Python: {self.os_manager.os_info.python_version}")
        print(f"✓ Voice: {'Human-Like Mode' if self.config.get('human_like_voice', True) else 'Standard Mode'}")
        print(f"✓ Music System: {'Ready' if YOUTUBE_DL_AVAILABLE else 'Limited'}")
        
        # Print available voices
        voices = self.enhanced_speech_manager.get_available_voices()
        print(f"✓ Available Voices: {len(voices)}")
        
        print(f"\n🎵 NEW MUSIC FEATURES:")
        print("  ✓ YouTube Music Playback")
        print("  ✓ Audio/Video Streaming")
        print("  ✓ Volume Control")
        print("  ✓ Search and Play")
        print("  ✓ Music History")
        print("  ✓ Trending Music")
        
        print(f"\n🗣️  VOICE ENHANCEMENTS:")
        print("  ✓ Human-Like Speech Mode")
        print("  ✓ Multiple Voice Styles")
        print("  ✓ Multi-Language Support")
        print("  ✓ Natural Pauses & Emphasis")
        print("  ✓ Adjustable Speech Rate")
        
        print(f"\n📋 ALL ORIGINAL FEATURES ACTIVE")
        print()
    
    def set_mode(self, mode: OperationMode):
        """Set operation mode"""
        self.operation_mode = mode
        self.enhanced_speech_manager.operation_mode = mode
    
    def speak(self, text: str, language: str = None, human_like: bool = None):
        """Enhanced speak method"""
        self.system_state = SystemState.SPEAKING
        self.enhanced_speech_manager.speak(text, language, human_like)
        self.system_state = SystemState.IDLE
    
    def listen(self, timeout: int = None) -> Optional[str]:
        """Listen for voice input safely"""
        if not self.recognizer:
            return None
        
        if timeout is None:
            timeout = self.config.get('listen_timeout', 5)
        
        self.system_state = SystemState.LISTENING
        
        try:
            print("🎤 Listening...")
            with self.mic as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.config.get('phrase_time_limit', 8)
                )
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.get('language', 'en')
                )
                print(f"✓ You: {text}")
                return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return None
        finally:
            self.system_state = SystemState.IDLE
    
    def hotword_listen(self) -> bool:
        """Listen for hotword safely"""
        if not self.recognizer:
            return False
        
        hotword = self.config.get('hotword', 'jarvis')
        try:
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio).lower()
                return hotword in text
        except:
            return False
    
    def process_command(self, command: str) -> Optional[str]:
        """Process command"""
        if not command:
            return None
        
        self.system_state = SystemState.PROCESSING
        self.stats['commands_processed'] += 1
        self.data_manager.log_command(command)
        
        # Add to context memory
        self.context_memory.add_interaction(command)
        
        # Process through command processor
        result = self.command_processor.process(command)
        
        if result == "SESSION_END":
            self.active_session = False
            result = "Session ended. Say my name when you need me, sir."
        elif not result:
            # No handler matched - use AI
            self.stats['ai_queries'] += 1
            result = self.ai.query(command)
        
        self.system_state = SystemState.IDLE
        return result
    
    def run_session(self):
        """Run active session"""
        greetings = [
            "I'm listening, sir. How may I assist you?",
            "At your service. What do you need, sir?",
            "Ready and waiting. What can I do for you, sir?",
            "Systems online. How can I help, sir?",
        ]
        self.speak(random.choice(greetings))
        
        while self.active_session and not self.shutdown_flag:
            try:
                command = self.listen()
                
                if command:
                    # Check for exit commands
                    if any(x in command for x in ["stop", "exit", "quit", "goodbye", "bye"]):
                        self.active_session = False
                        farewells = [
                            "Session ended. I'll be here when you need me, sir.",
                            "Signing off. Call me anytime, sir.",
                            "Going into standby mode. Just say my name when you're ready, sir.",
                            "Session closed. I'm always here if you need anything, sir.",
                        ]
                        self.speak(random.choice(farewells))
                        break
                    
                    # Process command
                    result = self.process_command(command)
                    if result:
                        self.speak(result)
            
            except KeyboardInterrupt:
                self.active_session = False
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                time.sleep(0.5)
    
    def run(self):
        """Main run loop"""
        startup_messages = [
            "JARVIS MARK I ENHANCED online and ready, sir. All systems operational.",
            "Good to see you, sir. JARVIS MARK I ENHANCED at your service.",
            "Systems initialized successfully. How may I assist you today, sir?",
            "JARVIS MARK I ENHANCED reporting for duty. Ready for your commands, sir.",
        ]
        self.speak(random.choice(startup_messages))
        
        try:
            while not self.shutdown_flag:
                try:
                    # Check system alerts
                    alerts = self.system_monitor.get_pending_alerts()
                    for alert in alerts:
                        if alert['level'] == 'critical':
                            self.speak(f"Alert, sir. {alert['message']}")
                    
                    # Listen for hotword
                    if self.hotword_listen():
                        print(f"\n✓ Activated!")
                        self.active_session = True
                        self.run_session()
                    
                    time.sleep(0.1)
                
                except KeyboardInterrupt:
                    self.shutdown_flag = True
                    break
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    time.sleep(0.5)
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown JARVIS"""
        print("\n⚡ Shutting down JARVIS MARK I ENHANCED...")
        shutdown_messages = [
            "Powering down systems. Goodbye, sir.",
            "Shutting down. It's been a pleasure serving you, sir.",
            "Going offline. Until next time, sir.",
            "Systems shutting down. Stay safe, sir.",
        ]
        self.speak(random.choice(shutdown_messages))
        time.sleep(2)
        
        # Stop all systems
        self.enhanced_speech_manager.stop()
        self.music_controller.stop()
        self.system_monitor.stop_monitoring()
        self.data_manager.shutdown()
        
        # Print statistics
        uptime = datetime.now() - self.stats['start_time']
        print("\n" + "="*60)
        print("  📊 SESSION STATISTICS")
        print("="*60)
        print(f"Uptime: {uptime}")
        print(f"Commands processed: {self.stats['commands_processed']}")
        print(f"AI queries: {self.stats['ai_queries']}")
        print(f"Music played: {self.stats['music_played']}")
        print("="*60 + "\n")
        print("✓ Shutdown complete.\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🤖 JARVIS MARK I - ENHANCED ULTIMATE EDITION")
    print("  Complete AI Assistant with Music & Enhanced Voice")
    print("  Created by Singh Industries")
    print("  Designed & Engineered by: Mr. Prabhnoor Singh")
    print("="*70)
    
    print("\n🎵 NEW MUSIC & VOICE FEATURES:")
    print("  ✓ YouTube Music Player (Play any song)")
    print("  ✓ Audio/Video Streaming (YouTube)")
    print("  ✓ Volume Control (0-100%)")
    print("  ✓ Search & Play (Instant playback)")
    print("  ✓ Music History (Track what you've played)")
    print("  ✓ Trending Music (Latest hits)")
    print("  ✓ Human-Like Voice (Natural speech)")
    print("  ✓ Multiple Voice Styles (Professional/Casual/Excited)")
    print("  ✓ Multi-Language TTS (30+ languages)")
    print("  ✓ Adjustable Speech Rate (Slow/Fast)")
    print("  ✓ Natural Pauses & Emphasis")
    
    print("\n🚀 ALL ORIGINAL FEATURES PRESERVED:")
    print("  ✓ WhatsApp Call Control")
    print("  ✓ System & Hardware Control")
    print("  ✓ File & Folder Management")
    print("  ✓ VS Code & Developer Tools")
    print("  ✓ Web & Search Automation")
    print("  ✓ Multi-Mode Operation")
    print("  ✓ Context Memory & References")
    print("  ✓ Safety Confirmations")
    print("  ✓ Weather Information")
    print("  ✓ System Monitoring")
    
    print("\n⚡ Starting JARVIS MARK I ENHANCED...")
    print("="*70 + "\n")
    
    # Check for required music packages
    if not YOUTUBE_DL_AVAILABLE:
        print("⚠️  yt-dlp not installed. Music features will be limited.")
        print("   Install with: pip install yt-dlp")
    
    if not VLC_AVAILABLE:
        print("⚠️  python-vlc not installed. Local playback will use browser.")
        print("   Install with: pip install python-vlc")
    
    if not GTTS_AVAILABLE:
        print("⚠️  gTTS not installed. Enhanced TTS features limited.")
        print("   Install with: pip install gtts")
    
    if not PLAYSOUND_AVAILABLE:
        print("⚠️  playsound not installed. Audio playback limited.")
        print("   Install with: pip install playsound")
    
    try:
        jarvis = JarvisMarkIEnhanced()
        jarvis.run()
    except KeyboardInterrupt:
        print("\n\n⚡ Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")