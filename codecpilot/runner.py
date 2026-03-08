import subprocess
import shlex
import os
from typing import List, Optional, Tuple

class EncodingError(Exception):
    def __init__(self, message: str, log_file: str):
        self.message = message
        self.log_file = log_file
        super().__init__(self.message)

def run_ffmpeg_command(command_str: str, progress_callback=None) -> Tuple[bool, Optional[str]]:
    """
    Run an FFmpeg command, capturing output.
    Returns (success, log_file_path).
    """
    # Parse the command string into a list
    try:
        cmd_list = shlex.split(command_str)
    except Exception as e:
        raise ValueError(f"Failed to parse command: {e}")
        
    if cmd_list[0] != "ffmpeg":
        cmd_list.insert(0, "ffmpeg")
        
    # We want to force ffmpeg to overwrite for testing
    if "-y" not in cmd_list:
        cmd_list.insert(1, "-y")
        
    log_file = "ffmpeg_error.log"
    
    # We'll run it synchronously for simplicity in this MVP, 
    # but capture stderr since ffmpeg prints everything there.
    try:
        result = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        # Success!
        return True, None
    except subprocess.CalledProcessError as e:
        # Write log to file so it can be debugged
        with open(log_file, "w") as f:
            f.write(e.stderr)
        raise EncodingError(f"FFmpeg encoding failed with exit code {e.returncode}", log_file)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg command not found. Please ensure FFmpeg is installed.")
