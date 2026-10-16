# Production details

Resolve the personal voice from the established `ELEVENLABS_VOICE_ID`. In this user's October 2026 workflow, the plugin sample `jB1Cifc2UQbq1gR3wnb0` was not the user's voice. Do not select it just because it is the default. Keep API keys out of episode JSON; a voice identifier may be stored as configuration.

Existing approved jobs used ElevenLabs `eleven_v4`, Korean, speed 1.10, stability 0.46, similarity 0.82, style 0.58, and speaker boost. Treat these as a starting configuration, not a requirement to retain an obsolete model. A key may allow synthesis without `voices_read`: inability to fetch voice metadata does not by itself show that the established voice cannot synthesize speech. Never change voice identity silently.

Record provider, voice-ID source, model, timing edits and final runtime. Retain the original take when editing pauses or shortening narration. Regenerate subtitle timings after audio changes.

Discover the installed Video Studio location rather than hardcoding a plugin cache version. Use its normal production, preview, QA and cue tools. A project-local runner may change its vertical preset's duration target/maximum for a requested 180-second Threads video while retaining codec/frame/audio validation. Do not mislabel it as a YouTube Short or modify shared plugin defaults.

## Local FFmpeg channel-layout issue

The installed Windows FFmpeg failed on an untagged stereo WAV with `loudnorm,...,aresample`: “Cannot select channel layout”. Preserve the completed video-only render and fix only audio/mux. Explicit stereo around normalization resolved it:

```text
aformat=channel_layouts=stereo,loudnorm=I=-14:TP=-1.8:LRA=11,aformat=sample_rates=48000:channel_layouts=stereo
```

Prefer measured two-pass normalization, retaining explicit stereo in the second pass. Encode AAC at 48 kHz, copy the completed video stream, pad only the planned audio tail, cut to the verified duration, and re-run final QA. Do not re-render all scenes for an audio mux error.

Keep the final MP4, exact caption, source links, voice provenance, QA, manifest/state and publication verification together. Updating local media does not replace a published video.
