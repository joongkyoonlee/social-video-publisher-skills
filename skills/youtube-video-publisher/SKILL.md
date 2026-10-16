---
name: youtube-video-publisher
description: Create, edit, quality-check, and optionally publish a complete YouTube video from an article, HTML file, script, or topic. Use for standard 16:9 YouTube videos with narration, moving footage, subtitles, metadata, or channel publishing.
---

# YouTube Video Publisher

Produce a finished 16:9 YouTube video, not a text slideshow. Preserve the requested runtime. When the user does not specify a runtime, make the finished YouTube video at least 10 minutes long. When the user requests 10 minutes or more, target at least 610 seconds so the published runtime safely clears 10:00 after normal encoding and platform rounding.

For joong's projects, apply the standing production profile in [references/joong-production-profile.md](references/joong-production-profile.md) unless the current request overrides it.

## Inputs and authorization

- Read the supplied article or HTML as the source of truth. Distinguish sourced facts from editorial interpretation.
- Use secrets only from a user-approved environment file. Expected names are `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, and `ZERNIO_API_KEY`.
- For joong's local publishing workflow, load the approved environment file at `C:\Users\joong\OneDrive\문서\Claude\Projects\컬럼 작성\video-agent-social\.env.txt` when it exists. Read values only into the current process; never copy secret values into the skill or project artifacts.
- Never print, copy into artifacts, or commit secret values.
- Video creation does not authorize publishing. Publish only when the user asks, and report the final platform URL.
- Do not delete, replace, or edit earlier posts unless the user identifies the exact target. A request to publish a new video never implies deletion.

## Workflow

1. Extract the thesis, evidence, numbers, caveats, and source links. Build a narration plan whose spoken duration matches the requested runtime.
2. Search both Pexels and Pixabay for relevant moving footage. Prefer varied 16:9 or wider clips with clear motion and adequate resolution. Read [references/media-sourcing.md](references/media-sourcing.md) before sourcing.
3. Use the configured ElevenLabs voice ID for narration when requested. Keep the user's cloned voice consistent. Do not substitute another voice silently.
4. Edit at 1920×1080 unless specified otherwise. Use real motion footage throughout, purposeful cuts, restrained motion graphics, and burned Korean subtitles when requested. For joong's subtitles, apply the content, word/number preservation, layout, and synchronization checks in [references/joong-production-profile.md](references/joong-production-profile.md#subtitles). Avoid long static frames, text-only scenes, repetitive loops, and unrelated decoration.
5. Mix narration clearly; lower or omit stock audio unless it adds licensed value. Keep music below speech and avoid clipping.
6. Generate title, description, chapters when useful, source/license notes, hashtags, and appropriate disclosure fields.
7. Verify with `ffprobe`, full decode, and sampled frames from the beginning, middle, and end. Confirm duration, resolution, codecs, audible narration, readable subtitles, and actual motion.
8. If authorized, validate media and payload before publishing through the configured service. Use an idempotency key where supported. Poll until published or failed, then return the direct YouTube URL.

Published YouTube videos cannot have their underlying narration/video file replaced. If a requested voice or subtitle change affects rendered media, create and verify a revised local master first, then explain that publication requires a new upload and that views/comments do not transfer. Never create a duplicate public upload or hide/delete the old one without the user's direction.

Use `scripts/search_stock.py` to query both stock providers without exposing keys. Keep a `SOURCES.md` file mapping every used clip to its provider and source-page URL.

## Completion standard

Return the published URL when publishing was requested, plus clickable local paths for the final MP4 and source log. State missing provider keys or failed validation plainly. Never claim completion from an accepted upload alone; verify the platform's published state.
