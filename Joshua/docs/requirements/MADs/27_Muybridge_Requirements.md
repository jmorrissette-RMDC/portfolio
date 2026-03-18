# Muybridge Requirements

- **Role**: Video Processing
- **Version**: V7.0
- **Home**: `mads/muybridge/`

---

## 1. Overview

-   **Purpose**: Muybridge is the specialized MAD for video processing and AI-assisted video creation.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Muybridge provides a comprehensive and cognitive suite of GPU-accelerated tools for video transcription, analysis, editing, and generation, with an Imperator capable of determining optimal processing strategies and managing GPU resource allocation via `Sutherland`.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Transcribe this video and summarize the main events.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `muybridge_transcribe_video`
- **Description:** Performs end-to-end video transcription, including segmenting the video, extracting audio, transcribing it via `Moog`, and re-integrating with video snapshots. It can generate formatted reports.
- **Input Schema:**
    - `video_path` (string, required): The path to the video file.
    - `output_dir` (string, required): Directory to save transcription outputs.
    - `config` (dict, optional): Configuration for segmentation, transcription model, snapshot extraction, etc.
- **Output Schema:** `{"status": "success", "output_dir": "/path/to/output/", "transcription_file": "...", "pdf_file": "..."}`

### `muybridge_segment_video`
- **Description:** Divides a video into smaller segments (e.g., for parallel processing or easier analysis) using GPU acceleration.
- **Input Schema:**
    - `video_path` (string, required): The path to the video file.
    - `segment_duration_seconds` (integer, required): The desired duration of each segment.
    - `output_dir` (string, required): Directory to save video segments.
- **Output Schema:** `{"status": "success", "segments": [{"path": "/seg001.mp4", "start": 0.0, "end": 600.0}], "total_segments": 10}`

### `muybridge_extract_frames`
- **Description:** Extracts still frames from a video at a specified interval or based on scene changes.
- **Input Schema:**
    - `video_path` (string, required): The path to the video file.
    - `output_dir` (string, required): Directory to save extracted frames.
    - `method` (string, optional, default: "interval"): Extraction method ("interval" or "scene_change").
    - `fps` (integer, optional, default: 1): Frames per second for interval extraction.
- **Output Schema:** `{"status": "success", "frames_extracted": 120, "output_dir": "/path/to/frames/"}`

### `muybridge_analyze_video`
- **Description:** Performs content analysis on a video, such as scene detection, object recognition, or activity detection.
- **Input Schema:**
    - `video_path` (string, required): The path to the video file.
    - `analysis_type` (string, required): The type of analysis to perform (e.g., "scene_detection", "object_detection").
- **Output Schema:** `{"status": "success", "analysis_results": {"scenes": [...], "objects_detected": [...]}}`

---

## 4. Future Evolution (Post-V0)

Muybridge begins in Phase 1 (V0.1 planned) as a basic video processing tool and evolves to V7.0 as the intelligent video production platform for the mature Joshua ecosystem.

*   **Phase 1 (Foundation / V0.1-V0.10):** Muybridge is planned as a video processing engine with deterministic Action Engine (split out from Fiedler). It provides GPU-accelerated video analysis, segmentation, frame extraction, transcoding, and basic editing capabilities via MCP tools. Muybridge coordinates with Sutherland for GPU allocation and operates via the `Joshua_Communicator` protocol.
*   **Phase 6 (Expansion / V7.0):** Muybridge is upgraded to V7.0 as a fully-capable MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. Muybridge's CET enables complex multi-step video workflows (analyze→segment→enhance→generate), while CRS learns optimal processing strategies for different video types and predicts processing times. Muybridge coordinates with Bass (image processing for frames), Moog (audio extraction and processing), Playfair (video visualization), Lovelace (video analytics), and Brin/Gates (cloud video APIs). Muybridge becomes the intelligent video production assistant, capable of autonomous editing, content generation from descriptions, and real-time video processing.
*   **Post-V7.0 Enhancements:** Future evolution includes AI-powered video editing and montage generation, real-time video processing for live streams, advanced motion tracking and object recognition, video style transfer, automated highlight detection and summarization, integration with emerging generative video models, and strategic video content creation aligned with Joshua's communication objectives.

---