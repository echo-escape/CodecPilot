import os
from typing import List, Optional
from google import genai
from codecpilot.models import VideoAnalysisInfo
from pydantic import BaseModel

class PromptContext(BaseModel):
    analysis: Optional[VideoAnalysisInfo] = None
    user_prompt: Optional[str] = None
    task_type: str  # e.g., "encode", "explain", "debug"
    context_data: Optional[str] = None

class LLMService:
    def __init__(self):
        # Assumes GEMINI_API_KEY is set in environment
        # We handle initialization gracefully if key is missing
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        # Using a reliable model like gemini-2.5-flash
        self.model_name = "gemini-2.5-flash"

    def _ensure_client(self):
        if not self.client:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to use AI features.")

    def generate_encode_command(self, analysis: VideoAnalysisInfo, user_prompt: str) -> List[str]:
        """Generate an FFmpeg command based on video metadata and user prompt."""
        self._ensure_client()
        
        system_instruction = (
            "You are an expert FFmpeg CLI engineer. "
            "You are given a JSON representation of a video's metadata and a user's prompt of what they want to achieve. "
            "IMPORTANT: Your response MUST be EXACTLY a valid FFmpeg command array separated by spaces, or exactly the command string. "
            "Return ONLY the FFmpeg arguments starting with 'ffmpeg -i INPUT_FILE ...'. "
            "Do NOT wrap it in Markdown formatting like ```bash. Just output the raw command. "
            "Do NOT explain the command unless asked."
        )
        
        prompt = (
            f"Here is the video metadata (JSON): \n{analysis.model_dump_json(indent=2)}\n\n"
            f"User request: {user_prompt}\n\n"
            f"The input filename in the command should be exactly: {analysis.format.filename}\n"
            "Write the ffmpeg command. "
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, # Low temp for deterministic CLI commands
            )
        )
        
        cmd_str = response.text.strip()
        # Clean up markdown if the model hallucinated it
        if cmd_str.startswith("```"):
            lines = cmd_str.split("\n")
            cmd_str = "".join([l for l in lines if not l.startswith("```")]).strip()
            
        return cmd_str

    def explain_parameter(self, param: str) -> str:
        """Explain an FFmpeg parameter."""
        self._ensure_client()
        
        prompt = (
            f"Please explain the FFmpeg parameter '{param}' in a clear, concise, and developer-friendly way. "
            "Include an example of how it is typically used in a command line."
        )
        
        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.5,
            )
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def debug_log(self, log_content: str) -> str:
        """Analyze an FFmpeg error log and suggest fixes."""
        self._ensure_client()
        
        prompt = (
            "You are an FFmpeg debugging expert. I ran an FFmpeg command and it failed. "
            "Here is the error log output:\n"
            "---------------------\n"
            f"{log_content[-3000:]}\n" # Just send the last 3000 chars to avoid token limits
            "---------------------\n"
            "Please analyze why it failed and suggest a specific fix or modified command."
        )
        
        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.3,
            )
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
