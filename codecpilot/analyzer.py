import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any

from codecpilot.models import VideoAnalysisInfo, FormatMetadata, VideoStream, AudioStream

class FFprobeError(Exception):
    """Raised when ffprobe execution fails."""
    pass

def run_ffprobe(file_path: str) -> Dict[str, Any]:
    """Run ffprobe on the given file and return the parsed JSON output."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise FFprobeError(f"ffprobe failed: {e.stderr}")
    except json.JSONDecodeError:
        raise FFprobeError("Failed to parse ffprobe JSON output")
    except FileNotFoundError:
        raise FFprobeError("ffprobe command not found. Please ensure FFmpeg is installed.")

def analyze_video(file_path: str) -> VideoAnalysisInfo:
    """Analyze a video file and return a structured VideoAnalysisInfo object."""
    raw_data = run_ffprobe(file_path)
    
    # Parse format
    fmt_data = raw_data.get("format", {})
    format_meta = FormatMetadata(
        filename=Path(file_path).name,
        nb_streams=int(fmt_data.get("nb_streams", 0)),
        format_name=fmt_data.get("format_name", "unknown"),
        format_long_name=fmt_data.get("format_long_name", "unknown"),
        duration=float(fmt_data.get("duration", 0.0)),
        size=int(fmt_data.get("size", 0)),
        bit_rate=int(fmt_data.get("bit_rate", 0)) if fmt_data.get("bit_rate") else None,
        tags=fmt_data.get("tags", {})
    )

    video_streams = []
    audio_streams = []

    # Parse streams
    for stream in raw_data.get("streams", []):
        codec_type = stream.get("codec_type")
        
        if codec_type == "video":
            video_streams.append(VideoStream(
                index=stream.get("index", 0),
                codec_name=stream.get("codec_name", "unknown"),
                width=stream.get("width", 0),
                height=stream.get("height", 0),
                display_aspect_ratio=stream.get("display_aspect_ratio"),
                pix_fmt=stream.get("pix_fmt"),
                color_range=stream.get("color_range"),
                color_space=stream.get("color_space"),
                color_transfer=stream.get("color_transfer"),
                color_primaries=stream.get("color_primaries"),
                profile=stream.get("profile"),
                level=stream.get("level"),
                bit_rate=stream.get("bit_rate"),
                r_frame_rate=stream.get("r_frame_rate"),
                avg_frame_rate=stream.get("avg_frame_rate")
            ))
        elif codec_type == "audio":
            audio_streams.append(AudioStream(
                index=stream.get("index", 0),
                codec_name=stream.get("codec_name", "unknown"),
                sample_rate=stream.get("sample_rate"),
                channels=stream.get("channels"),
                bit_rate=stream.get("bit_rate"),
                language=stream.get("tags", {}).get("language")
            ))

    return VideoAnalysisInfo(
        file_path=file_path,
        format=format_meta,
        video_streams=video_streams,
        audio_streams=audio_streams,
        raw_ffprobe_data=raw_data
    )
