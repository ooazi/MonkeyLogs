import os
import time
import json
from collections import defaultdict
from AppKit import NSApplication, NSApp
from Foundation import NSObject
from Cocoa import NSEvent, NSKeyDownMask
from PyObjCTools import AppHelper

# Configuration for local logging
DIRECTORY = os.path.expanduser("~/monkeylogger/monkeylogs/log")  
FILENAME = "log.jsonc"
AFK_THRESHOLD = 5  # Time in seconds before considering AFK

# Typing statistics
total_keystrokes = 0
keystroke_times = []
key_frequencies = defaultdict(int)
last_keystroke_time = None  # Track last activity to detect AFK

def get_log_path():
    """Ensures the log directory exists and returns the full log file path."""
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    return os.path.join(DIRECTORY, FILENAME)

def initialize_log():
    """Creates the log file if it doesn't exist or is corrupted."""
    log_path = get_log_path()
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                data = json.load(f)
                if "sessions" not in data:  # Fix missing key
                    data["sessions"] = []
        else:
            data = {"sessions": []}

        # Overwrite log file with corrected data
        with open(log_path, "w") as f:
            json.dump(data, f, indent=4)
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️ Log file corrupted or missing. Resetting log.")
        data = {"sessions": []}
        with open(log_path, "w") as f:
            json.dump(data, f, indent=4)

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        mask_down = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask_down, key_handler)

def key_handler(event):
    global total_keystrokes, keystroke_times, key_frequencies, last_keystroke_time

    try:
        key_pressed = event.characters()
        if key_pressed:
            total_keystrokes += 1
            key_frequencies[key_pressed] += 1  # Track key usage

            # Track keystroke timing
            current_time = time.time()
            if last_keystroke_time is not None:
                elapsed_time = current_time - last_keystroke_time

                # **Ignore AFK time (if elapsed time is greater than the AFK threshold)**
                if elapsed_time <= AFK_THRESHOLD:
                    keystroke_times.append(elapsed_time)

            last_keystroke_time = current_time  # Reset AFK timer

        # Every 30 keystrokes, log session stats
        if total_keystrokes % 30 == 0:
            log_results()
    except KeyboardInterrupt:
        AppHelper.stopEventLoop()

def calculate_wpm():
    """Calculates Words Per Minute (WPM) based on keystrokes and valid session duration."""
    session_duration = sum(keystroke_times) if keystroke_times else 0
    wpm = (total_keystrokes / 5) / (session_duration / 60) if session_duration > 0 else 0
    return round(wpm, 2)

def calculate_stats():
    """Calculates statistics based on typing session data."""
    session_duration = sum(keystroke_times) if keystroke_times else 0
    avg_keystroke_time = (session_duration / len(keystroke_times)) if keystroke_times else 0
    wpm = calculate_wpm()
    
    return {
        "timestamp": int(time.time()),
        "total_keystrokes": total_keystrokes,
        "wpm": wpm,
        "session_duration": round(session_duration, 2),  # **Only counts active typing time**
        "avg_keystroke_time": round(avg_keystroke_time, 3),
        "most_used_keys": dict(sorted(key_frequencies.items(), key=lambda item: item[1], reverse=True)[:5])  # Top 5 keys
    }

def log_results():
    """Logs typing session statistics securely."""
    log_path = get_log_path()
    try:
        initialize_log()  # Ensure the file exists and is valid

        with open(log_path, "r") as f:
            data = json.load(f)

        stats = calculate_stats()
        data["sessions"].append(stats)

        with open(log_path, "w") as f:
            json.dump(data, f, indent=4)
            
        print(f"📝 Logged Stats: {stats}")
    except Exception as e:
        print(f"⚠️ Error logging results: {e}")

if __name__ == '__main__':
    print("🔴 Keylogger running... Logging secure typing statistics.")
    initialize_log()  # Ensure log file exists before starting
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()