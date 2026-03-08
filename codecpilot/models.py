from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AudioStream(BaseModel):
    index: int
    codec_name: str
    codec_type: str = "audio"
    sample_rate: Optional[str] = None
    channels: Optional[int] = None
    bit_rate: Optional[str] = None
    language: Optional[str] = None

class VideoStream(BaseModel):
    index: int
    codec_name: str
    codec_type: str = "video"
    width: int
    height: int
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[str] = None  # Color space/pixel format e.g. yuv420p
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    color_primaries: Optional[str] = None
    profile: Optional[str] = None
    level: Optional[int] = None
    bit_rate: Optional[str] = None
    r_frame_rate: Optional[str] = None  # Framerate e.g. 60000/1001
    avg_frame_rate: Optional[str] = None

class FormatMetadata(BaseModel):
    filename: str
    nb_streams: int
    format_name: str
    format_long_name: str
    duration: float
    size: int
    bit_rate: Optional[int] = None
    tags: Dict[str, str] = Field(default_factory=dict)

class VideoAnalysisInfo(BaseModel):
    file_path: str
    format: FormatMetadata
    video_streams: List[VideoStream] = Field(default_factory=list)
    audio_streams: List[AudioStream] = Field(default_factory=list)
    raw_ffprobe_data: Dict[str, Any] = Field(default_factory=dict)
