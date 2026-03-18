# Bass Requirements

- **Role**: Image Processing & Computer Vision
- **Version**: V7.0
- **Home**: `mads/bass/`

---

## 1. Overview

-   **Purpose**: Bass is the specialized MAD for image processing, computer vision, and AI-assisted image generation.
-   **V7.0 Scope Definition**: As a V7.0 MAD, Bass provides a comprehensive suite of GPU-accelerated tools for image analysis, transformation, enhancement, and generation, all accessible via a cognitive, conversational interface.

---

## 2. Tool Exposure Model

This MAD follows the Direct Tool Exposure architecture (ADR-023). Its public tools are exposed directly on its MCP server and are discoverable via the Rogers registry. Any incoming communication that is not a valid MCP call for an exposed tool is routed to the Thought Engine for conversational processing (e.g., "Enhance this photo to look more professional.").

> **Note on Tool List:** The tools listed in this document are a *provisional set* based on the MAD's high-level requirements. The final, authoritative list of tools, their specific parameters, and their return schemas will be defined in a dedicated Design Document prior to implementation.

---

## 3. Public Action Engine Tools

### `bass_analyze_image`
- **Description:** Performs a comprehensive analysis of an image, extracting metadata, detecting objects, and assessing quality.
- **Input Schema:**
    - `image_path` (string, required): The path to the image file.
    - `analysis_options` (array[string], required): A list of analyses to perform (e.g., `["metadata", "objects", "quality", "text"]`).
- **Output Schema:** `{"status": "success", "analysis": {"metadata": {...}, "objects": [...], ...}}`

### `bass_transform_image`
- **Description:** Performs standard image transformations like resizing, cropping, rotating, and format conversion.
- **Input Schema:**
    - `image_path` (string, required): The path to the source image.
    - `output_path` (string, required): The path to save the transformed image.
    - `operations` (array[dict], required): A list of transformation operations to apply (e.g., `[{"type": "resize", "width": 800}, {"type": "format", "format": "webp"}]`).
- **Output Schema:** `{"status": "success", "output_path": "/path/to/transformed.webp"}`

### `bass_enhance_image`
- **Description:** Applies AI-powered enhancements to an image, such as upscaling, denoising, or color correction.
- **Input Schema:**
    - `image_path` (string, required): The path to the source image.
    - `output_path` (string, required): The path to save the enhanced image.
    - `enhancements` (array[dict], required): A list of enhancements to apply (e.g., `[{"type": "upscale", "factor": 2, "model": "realesrgan"}]`).
- **Output Schema:** `{"status": "success", "output_path": "/path/to/enhanced.png"}`

### `bass_generate_image`
- **Description:** Generates an image from a text prompt using an AI model.
- **Input Schema:**
    - `prompt` (string, required): The text prompt describing the desired image.
    - `output_path` (string, required): The path to save the generated image.
    - `parameters` (dict, optional): Model-specific parameters like resolution, steps, seed, etc.
- **Output Schema:** `{"status": "success", "output_path": "/path/to/generated.png"}`

---

## 4. Future Evolution (Post-V0)

Bass is introduced in Phase 6 (Expansion) at V7.0 as the specialized image processing and computer vision platform for the mature Joshua ecosystem.

*   **Phase 6 (Expansion / V7.0):** Bass enters the ecosystem as a fully-capable V7.0 MAD with complete PCP (DTR, LPPM, CET, CRS), pure Kafka conversation bus integration, and eMAD awareness. As the vision specialist, Bass provides GPU-accelerated image analysis, transformation, enhancement, and AI-assisted image generation. Bass coordinates with Muybridge (video processing), Playfair (visualization), Sutherland (GPU allocation), and domain-specific MADs for comprehensive visual intelligence capabilities. Bass's CET enables complex multi-step image workflows, while CRS learns optimal processing pipelines based on content patterns.
*   **Post-V7.0 Enhancements:** Future evolution includes advanced AI model integration (ControlNet, Stable Diffusion variants, custom vision models), real-time image processing streams, integration with Brin/Gates for cloud vision APIs, and sophisticated image understanding capabilities supporting Lovelace's data visualization needs and Knuth's documentation diagram generation.

---