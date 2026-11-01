# YouTube upload setup (one time, free, no credit card)

The `upload` workflow uploads one ready story a day to PandaNanoAdventures as a **private** video, then opens an issue so you can watch it and publish it. Until the secrets below exist, it opens an "Upload by hand" issue with the download link and the text to paste instead.

## 1. Google Cloud (console.cloud.google.com)
1. Create a project (`blocky-stories`). Skip any billing or free-trial prompt, because none is needed.
2. APIs & Services → Library → **YouTube Data API v3** → Enable.
3. OAuth consent screen ("Google Auth Platform"): External, your email as support and developer contact. Add the scopes `youtube.upload` and `youtube.readonly`. Add yourself as a test user, then **Publish app** (In production). In Testing mode, the token dies every 7 days.
4. Clients → Create OAuth client → **Web application**, with the redirect URI `https://developers.google.com/oauthplayground`.

## 2. Refresh token (browser only)
At https://developers.google.com/oauthplayground:
1. Gear icon → "Use your own OAuth credentials" → paste the client ID and secret.
2. Scopes: `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly` → Authorize. Pick the **PandaNanoAdventures** channel and click through "unverified app".
3. Exchange the code for tokens and copy the **refresh token**.
4. Check: GET `https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true` shows PandaNanoAdventures. Note its `id` (UC...).

## 3. GitHub (repo → Settings)
- Secrets and variables → Actions → **Secrets**: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
- **Variables**: `YT_CHANNEL_ID` = the UC... id. The workflow refuses to upload if the token belongs to any other channel.
- Actions → General → Workflow permissions: **Read and write**.

## 4. The API audit
YouTube locks videos uploaded by an unaudited API project as private. You're publishing by hand anyway, but a locked video can't be made public. Fill in the free audit form at https://support.google.com/youtube/contact/yt_api_form ("a private tool that uploads my own videos to my own channel"). Until it's approved, use each issue's download link to upload by hand.

## Quota
The free quota is 10,000 units a day, and an upload costs about 1,600, so one a day is far inside it.
