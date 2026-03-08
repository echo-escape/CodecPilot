<div align="center">
  <h1>🚀 CodecPilot</h1>
  <p><b>The AI-Native FFmpeg Wrapper for Modern Video Engineering</b></p>
  <p>
    <a href="https://github.com/echo-escape/CodecPilot/tags"><img src="https://img.shields.io/github/v/tag/echo-escape/CodecPilot?color=blue&label=Version" alt="Version"></a>
    <a href="https://github.com/echo-escape/CodecPilot/actions"><img src="https://img.shields.io/github/actions/workflow/status/echo-escape/CodecPilot/ci.yml?branch=master" alt="Build Status"></a>
    <a href="https://github.com/echo-escape/CodecPilot/blob/master/LICENSE"><img src="https://img.shields.io/github/license/echo-escape/CodecPilot" alt="License"></a>
  </p>
</div>

---

## 🌩️ The Pain Point: Video Processing is Broken

For decades, **FFmpeg** has been the undisputed king of video and audio processing. However, integrating it into modern production pipelines reveals massive developer experience (DX) bottlenecks:

1. **Arcane Syntax**: Crafting the perfect FFmpeg command requires encyclopedic knowledge of codecs, containers, and hundreds of undocumented flags.
2. **Cryptic Errors**: When an encode fails due to color space mismatch or b-frame pyramid issues, the logs are dense, unreadable, and offer zero actionable fixes.
3. **Static Pipelines**: Traditional encoding scripts fail when ingested media varies in resolution, color depth, or framerate—requiring constant, manual intervention.

## 💡 The Solution: CodecPilot

**CodecPilot** is a terminal-native, AI-powered CLI wrapper that revolutionizes how developers interact with FFmpeg. By leveraging Large Language Models (LLMs), it acts as an autonomous encoding engineer that sits directly in your workflow.

Instead of wrestling with syntax, you declare your *intent*. CodecPilot analyzes the source file, calculates the optimal parameters based on your goals, and executes the perfect command.

### Key Capabilities
- **Semantic Encoding**: Generate complex FFmpeg commands using natural language (e.g., *"Encode this for Twitter mobile, prioritize quality but keep it under 50MB"*).
- **Intelligent Diagnostics**: Feed an FFmpeg crash log to `codecpilot debug`, and instantly receive root-cause analysis and the exact command to fix it.
- **Deep Metadata Analysis**: Extracts and formats rich video/audio topology overviews far cleaner than standard `ffprobe`.
- **Parameter Explainability**: Ask CodecPilot to explain what `b_pyramid` or `pix_fmt yuv422p10le` actually does under the hood.

## 🛠️ Use Cases

### 1. Daily Developer Workflows
Say goodbye to StackOverflow. Use CodecPilot directly in your terminal to rapidly prototype encoding pipelines, compress proxy media, or transcode messy user-generated content (UGC) into standardized formats.

### 2. Automated Media Ingestion
Integrate CodecPilot into your backend microservices. On uploading a video, CodecPilot can analyze the asset and dynamically generate a tailored, multi-bitrate HLS/DASH encoding ladder specifically optimized for that individual file's complexity.

### 3. GitHub PR Workflows (CI/CD Integration)
**CodecPilot natively supercharges your Pull Request workflows.** 
You can run CodecPilot in your GitHub Actions as an automated QA engineer for media-heavy PRs. 
- **Auto-Review**: When a PR modifies an FFMPEG script, CodecPilot can dry-run the command against a test matrix and comment on potential inefficiencies or compatibility issues.
- **Regression Testing**: If a nightly encoding job fails, CodecPilot automatically parses the `ffmpeg_error.log`, pushes a commit with the proposed fix, and creates a PR for human review.

## 🚀 Quick Start

### Prerequisites
CodecPilot requires an active **OpenAI API Key** to power its reasoning engine. Because it performs complex log analysis and configuration synthesis, **API credits are required** for operation. We highly recommend using `gpt-4o` for optimal reasoning capabilities.

```bash
# Export your OpenAI API key
export OPENAI_API_KEY="sk-proj-..."
```

*(Note: We actively welcome support and grants from OpenAI to subsidize inference costs for the broader open-source community.)*

### Installation

```bash
# Clone the repository
git clone https://github.com/echo-escape/CodecPilot.git
cd CodecPilot

# Install via pip
pip install -e .
```

### Usage Examples

**1. Analyze a video cleanly:**
```bash
codecpilot analyze input.mp4
```

**2. Natural Language Encoding:**
```bash
codecpilot encode input.MOV --prompt "Convert this to a highly compressed webm for Discord, remove audio"
```

**3. Debugging a crashed encode:**
```bash
codecpilot debug ffmpeg_crash_report.log
```

---
Built for the open-source community. Let's make video engineering accessible to everyone.
