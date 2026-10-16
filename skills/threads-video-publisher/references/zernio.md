# Zernio Threads flow

Official references checked 2026-10-16:
- https://docs.zernio.com/platforms/threads
- https://docs.zernio.com/media/get-media-presigned-url
- https://docs.zernio.com/guides/media-uploads

Prefer a connected Zernio tool when available, otherwise use the helper with `ZERNIO_API_KEY`. This account's API base is `https://zernio.com/api/v1`.

- `GET /accounts`: choose an active Threads account without `needsReconnection`. This workspace used `@joongkyoon`; confirm its live identifier instead of hardcoding a database ID.
- `POST /media/presign` with `{filename, contentType:"video/mp4", size}`; PUT the bytes to `uploadUrl` with matching headers, then use `publicUrl`. A Drive/OneDrive sharing page is not a usable media URL.
- `POST /posts`: exact caption in `content` and platform `customContent`; one `{platform:"threads",accountId:...}` entry; one `{type:"video",url:...}` in `mediaItems`; `publishNow:true` for authorized immediate publishing.
- `GET /posts/{postId}`: inspect the Threads platform's status, error, URL and registered caption. Successful responses here exposed `post._id`, `post.status`, `post.platforms[].status`, and `platformPostUrl`.

Persist artifact fingerprint, selected account, exact caption, media URL, create-started marker and returned post ID. Idempotency keys supplement reconciliation; they do not justify blind create retries. If a create request times out without an ID, inspect Zernio's recent posts for the exact account/caption/media and attach the confirmed ID to the manifest's state. Stop creating until resolved. With a known ID, use `verify`; a processing timeout means pending rather than failed.

Public pages may return a login shell or access restriction. Track HTTP accessibility separately from API publication, caption/media matching and actual playback inspection. Never claim playback review from HTTP 200.

The documented Threads API does not edit published posts. A follow-up reply, deletion or replacement is a separate public action requiring applicable authorization.
