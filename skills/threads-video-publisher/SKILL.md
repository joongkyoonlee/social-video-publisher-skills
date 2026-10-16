---
name: threads-video-publisher
description: Create, revise, quality-check, and publish Threads videos with platform-specific captions through Zernio. Use for 쓰레드 영상 제작, 3분 세로 영상, or publishing an existing video to Threads; keep other platforms out of scope unless requested.
---

# Threads Video Publisher

Produce a finished Threads video and caption, or publish a supplied finished video. Honor the current runtime, style, voice, account, and existing publication authorization. Creating this skill does not authorize demonstration posts or reposting earlier work.

## Production

- Read supplied source material and verify time-sensitive facts. Preserve qualifications and distinguish commentary from evidence. Do not animate source pages as a slideshow.
- For new video, use the installed Video Studio `start-here` and relevant production skill; apply `future-video-style` when available. Preserve the chosen graphic, source-card, footage, or mixed style. For a finished supplied video, skip unnecessary production work.
- This user's fallback is 3 minutes, 1080×1920, 30 fps; explicit requests override it. A Threads video is not limited to Video Studio's 60-second Shorts preset. Use a project-local duration configuration, retaining other QA, instead of weakening shared plugin defaults.
- Use ElevenLabs for requested narration and resolve `ELEVENLABS_VOICE_ID` from the established approved publishing setup. Never substitute the plugin's example voice for the user's own voice. Reuse a previously approved voice; if it cannot be established, ask for its registered name or ID while continuing independent visual work. Do not create a new clone without a request.
- Read credentials only into the process environment. The established approved file here is `C:\Users\joong\OneDrive\문서\Claude\Projects\컬럼 작성\video-agent-social\.env.txt`. Never copy secret values into this skill, manifests, or logs. Prefer a valid process API key over an obsolete file key while keeping the approved voice ID consistent.
- Preserve natural sentence/topic pauses, accurate subtitles, and modest pitch-preserving timing adjustments. Meet runtime through useful content, not blank holds or extreme stretching.

Read [references/production.md](references/production.md) for voice identity, longer vertical videos, and the local audio mux workaround. Follow production review gates within existing approvals; do not repeatedly ask for approvals already granted.

## Threads caption

Save the exact caption in `caption.txt`: concise hook and takeaway, material qualification, useful topic tags, and an existing source/full-video link when helpful. Add an AI voice/reconstruction notice when applicable. Count links and hashtags within the documented 500-character limit. Put longer sources in an existing linked full-video description or another requested destination; do not create extra replies or websites without authorization.

Use this short caption in Threads `customContent`, not a long YouTube description. When asked whether explanations were included, read back the registered published caption rather than only local metadata.

## Validate and publish

Read [references/zernio.md](references/zernio.md) for the API and recovery rules; refresh official requirements when they may have changed. Current documented video constraints: one H.264/AAC MP4, up to 5 minutes and 1 GB.

1. Check the requested runtime, codecs, synchronization, actual motion, text fit, start/end frames, representative encoded frames, and correct user voice. Run the production tool's loudness/peak QA.
2. Prepare and inspect the exact video/caption/account manifest. The helper's `prepare` and default `publish` are local checks; `accounts` is read-only.
3. Publish only with current user authorization. “Make and publish” already authorizes the requested destination; do not insert a redundant permission question. Show the completed artifact first when the production skill requires it. Clarify genuinely ambiguous accounts.
4. Run the helper with `--execute` only for that authorized artifact. Preserve its journal and idempotency key. Resume an existing post ID with `verify`. If a create request times out without returning an ID, reconcile it through Zernio before any new create request.
5. Require published platform status and the direct Threads URL; compare the registered caption. Record public URL accessibility separately. A generic HTTP 200 shell does not prove correct media or playback. Report any inspection limitation accurately.

Return the published URL and concise validation result, or the final local video/caption when posting was not requested. Never delete/hide a previous post or create a replacement public upload without applicable authorization. A local revision does not update an already published video.

## Helper

```text
python scripts/threads_publish.py accounts --env-file APPROVED_ENV
python scripts/threads_publish.py prepare --video FINAL_MP4 --caption-file CAPTION_TXT --account USERNAME --target-seconds 180 --output MANIFEST_JSON
python scripts/threads_publish.py publish MANIFEST_JSON --env-file APPROVED_ENV
python scripts/threads_publish.py publish MANIFEST_JSON --env-file APPROVED_ENV --execute
python scripts/threads_publish.py verify MANIFEST_JSON --env-file APPROVED_ENV
```

No upload occurs without `--execute`. The helper handles a single video post; text-only posts, reply chains, and other platforms need separately scoped work.
