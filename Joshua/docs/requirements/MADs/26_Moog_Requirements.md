# Moog Requirements

- **Role**: Audio Processing & Speech
- **Version**: V7.0
- **Home**: `mads/moog/`

---

## 1. Overview

-   **Purpose**: Moog is the specialized MAD for audio processing, speech recognition, and AI-assisted sound creation.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Moog provides a comprehensive and cognitive suite of GPU-accelerated tools for audio transcription, analysis, enhancement, and generation, with an Imperator capable of determining optimal processing strategies.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Transcribe this audio file and summarize the key points.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `moog_transcribe_audio`
- **Description:** Performs speech-to-text transcription of an audio file using advanced AI models (e.g., Whisper), with optional speaker diarization and timestamps.
- **Input Schema:**
    - `audio_path` (string, required): The path to the audio file.
    - `options` (dict, optional): Transcription options (e.g., `{"model": "whisper-large-v3", "language": "en", "enable_diarization": true}`).
- **Output Schema:** `{"status": "success", "transcription": "...", "segments": [...], "duration_seconds": 120.5}`

### `moog_analyze_audio`
- **Description:** Performs comprehensive audio content and feature analysis, including classification (music, speech, noise), tempo, key, and spectral analysis.
- **Input Schema:**
    - `audio_path` (string, required): The path to the audio file.
    - `analysis_type` (string, required): The type of analysis to perform (e.g., "full", "music_features", "speech_content").
- **Output Schema:** `{"status": "success", "content_type": "music", "features": {"tempo_bpm": 120.5, ...}}`

### `moog_enhance_audio`
- **Description:** Applies audio enhancements such as noise reduction, normalization, equalization, and dynamic range processing.
- **Input Schema:**
    - `audio_path` (string, required): The path to the source audio file.
    - `output_path` (string, required): The path to save the enhanced audio.
    - `enhancements` (array[dict], required): A list of enhancement operations (e.g., `[{"type": "noise_reduction", "strength": 0.7}]`).
- **Output Schema:** `{"status": "success", "output_path": "/path/to/enhanced.wav"}`

### `moog_synthesize_speech`
- **Description:** Generates speech from text using text-to-speech (TTS) models, with configurable voice, emotion, and speaking parameters.
- **Input Schema:**
    - `text` (string, required): The text to synthesize.
    - `voice` (string, optional): The voice ID to use (e.g., "en-US-Neural2-A").
    - `output_path` (string, required): The path to save the generated audio.
    - `parameters` (dict, optional): Voice synthesis parameters (e.g., `{"speed": 1.0, "emotion": "neutral"}`).
- **Output Schema:** `{"status": "success", "output_path": "/path/to/speech.mp3", "duration_seconds": 3.5}`

### `moog_generate_audio`
- **Description:** Generates audio content (e.g., music, sound effects) from a natural language prompt using AI models.
- **Input Schema:**
    - `prompt` (string, required): The text prompt describing the desired audio.
    - `output_path` (string, required): The path to save the generated audio.
    - `parameters` (dict, optional): Model-specific parameters.
- **Output Schema:** `{"status": "success", "output_path": "/path/to/generated_music.mp3"}`

---

## 4. Future Evolution (Post-V0)

Moog is introduced in Phase 6 (Expansion) at V7.0 as the specialized audio processing and speech platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Moog enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the audio specialist, Moog provides audio transcription, analysis, transformation, enhancement, and AI-assisted audio creation with GPU-accelerated processing via Sutherland coordination. Moog's CET enables complex multi-step audio workflows (transcribe→analyze→enhance→generate), while CRS learns from audio processing patterns to optimize pipelines based on content type and quality requirements. Moog coordinates with Muybridge (video audio extraction), Playfair (waveform visualization), Lovelace (audio analytics), and Brin/Gates (cloud speech APIs).
*   **Post-V7.0 Enhancements:** Future evolution includes real-time multilingual transcription, advanced speaker diarization, emotion detection and sentiment analysis, voice cloning and synthesis, music generation, audio restoration and enhancement, spatial audio processing, and AI-powered audio content creation aligned with Joshua's content objectives. Moog becomes the central hub for all audio intelligence in the ecosystem.

---