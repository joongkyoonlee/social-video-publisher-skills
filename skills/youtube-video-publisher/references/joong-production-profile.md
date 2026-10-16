# Joong production profile

Apply these defaults only to joong's local video workflow. A current user request always overrides them.

## Narration

- Use the approved ElevenLabs voice ID with a light, bright, lively, gently cheerful Korean explainer delivery. Keep a subtle smile in the voice and make the presentation feel conversational and enjoyable without sounding like an advertisement.
- Avoid sleepy, heavy, solemn, flat, or slow documentary delivery. Use crisp articulation, energetic sentence openings, varied pitch and emphasis, and confident sentence endings.
- Start near 1.10× normal delivery speed, typically within 1.08–1.12×, but retain natural pauses of about 120–220 ms at commas, 300–500 ms between sentences, and 550–900 ms at paragraph or topic changes. Gain speed from word delivery and editing rather than removing meaningful pauses.
- Reject narration that sounds like uninterrupted AI reading. Give key facts and concluding phrases clear emphasis and a firm finish, and vary cadence so consecutive sentences do not repeat the same contour.
- Starting voice settings: `stability: 0.46`, `similarity_boost: 0.82`, `style: 0.58`, `use_speaker_boost: true`. Treat these as a tested starting point, not an immutable requirement.
- Normalize finished narration to a clear speech-first mix and verify that it remains intelligible on phone speakers.
- Before a full render, listen to a representative 30–60 second sample. If it feels sleepy, grave, mechanical, or breathless, revise the delivery or voice settings first.

## Subtitles

- Use high-contrast Korean subtitles that avoid faces and interface zones.
- Default long-form subtitle size is about 10% smaller than the former 42-point baseline; use 38 at 1920×1080 unless a visual check calls for a nearby adjustment.
- Break captions and display lines only at whitespace or complete phrase boundaries. Never split a Korean eojeol, a proper name, or a number with its unit between lines or cues. If an indivisible token is too wide, adjust layout or font size instead of cutting it.
- Start with about 28 characters per cue (including spaces); flag cues over 34 characters for reflow or review. Use at most two display lines. Character limits are a drafting aid, not proof that rendered text fits.
- Preserve numbers exactly, including decimals, thousands separators, percentages, dates, and units. Treat `35.5%`, `1,000`, and `10.2초` as intact tokens; sentence splitting must not treat their punctuation as sentence boundaries. Never strip leading digits with a blanket heading-number regex. Remove section numbering only from explicitly identified heading markup.
- Prepare narration and captions from reviewed article text. Exclude HTML head/style/script/navigation and source-list boilerplate before extracting text. Match complete tag names or use a DOM parser; a paragraph matcher must not accidentally match `<html>`. Reject CSS/code leakage before sending text to speech synthesis.
- Compare the complete caption sequence against the reviewed narration script, allowing only documented pronunciation/display differences and whitespace changes. Check for missing or duplicated words and changed numbers. CSS keyword checks alone do not establish content correctness.
- Align cues to the actual spoken audio using speech timestamps or forced alignment when available. Character-proportional timing is only a draft; inspect and correct speech/caption synchronization before claiming it is verified.
- Use explicit subtitle canvas dimensions and safe margins. With ASS/libass, set PlayResX/PlayResY to the intended canvas and inspect actual font size; an SRT override of `FontSize=38` alone does not guarantee a 38-pixel result at 1920×1080. Ensure automatic wrapping also preserves whole words.
- After rendering, inspect beginning/middle/end frames plus the longest cues, two-line cues, numeric cues, and wrap transitions. Confirm complete glyphs inside the safe area, comfortable size, readable contrast, and no face/interface obstruction. Where available, check rendered text bounds for every cue; otherwise state the sample coverage and do not claim zero clipping throughout solely from a character-count check.
- Record content, number-preservation, word-boundary, visual-layout, and synchronization checks separately. Full video decode verifies file integrity, not subtitle accuracy. Unresolved content or clipping errors fail subtitle QA and must be corrected before calling the master ready to publish.

## Thumbnail and title packaging

- Create a custom thumbnail for every video. The title/hook must be visible immediately in the feed: one idea, usually two short lines, large bold Korean type, thick dark outline/shadow, and strong white plus neon-lime contrast.
- Use a single clear focal subject and keep the composition readable at about 120 px wide. The focal subject may be a person, object, place, symbolic scene, or topic-specific visual; a face is not required.
- Do not default to joong's portrait and do not use it repeatedly across a batch. Prefer topic-first imagery. In a multi-video batch, keep joong's face to a clear minority—normally no more than about 20% of thumbnails and never on consecutive releases—unless the current request explicitly asks for more.
- When joong's face is genuinely useful for channel identity or personal commentary, preserve the exact face, glasses, age, hair, and recognizability; never substitute a generated stranger. Cropping, background replacement, color grading, lighting enhancement, stylistic transformation, and mild retouching are allowed when they remain recognizable, respectful, and truthful to the topic.
- A well-known person may be the focal subject only when directly relevant to the video's subject and when the specific image is lawfully usable. Do not assume an image is free because the person is famous or the image appears in search results. Use public-domain material, a stock/editorial license that permits the intended YouTube use and transformations, or another documented permission; also consider applicable personality, publicity, and endorsement rights. Do not imply that the person endorses joong or the video.
- Record the source page, creator/provider, and license or permission basis for every third-party thumbnail image. If copyright or personality-right status is uncertain, use a licensed stock image, public-domain alternative, original graphic, or non-person topic visual instead.
- Use the skill-owned portrait assets in `../assets/joong-portraits/` so the workflow does not depend on the original document folder:
  - `portrait-grid.png`
  - `portrait-doc-01.png` through `portrait-doc-05.png`
- Treat these images as optional identity references and reusable source assets, not the default thumbnail source. Do not alter or overwrite the masters; write crops, cutouts, and composites to the current project's output folder.
- When a batch includes joong portraits, choose a pose and expression that fit the selected topics and do not reuse the same pose when alternatives exist.
- When joong's face appears, vary facial expressions and mix casual clothing with formal looks across releases. Do not default to the same neutral expression, dark suit, or repeated pose. Match the expression and outfit to the topic while preserving exact identity and a credible professional image.
- Before approval or publication, review the batch as a contact sheet. Reject a set that feels like the same portrait template repeated, even if each individual thumbnail is technically acceptable.
- Keep the platform title concise enough to display meaningfully before truncation. After publishing or updating, verify the public title and that the custom thumbnail endpoint returns successfully.
