# Privacy policy

Last updated: November 2, 2026

This covers "blocky-stories uploader", a small tool I wrote to upload my own animated shorts to my YouTube channel, Panda Nano Adventures (@pandananoadventures). It runs as a GitHub Actions workflow in this repo (`.github/workflows/upload.yml` and `scripts/upload.py`).

## Who uses it
Just me. Nobody else can sign in to it or connect an account to it. There's no website or app for anyone else to use.

## What it can access
It uses the YouTube API Services, only on my own channel, with two permissions:
- `youtube.upload`, to upload my videos (`videos.insert`)
- `youtube.readonly`, to check it's signed in to my channel before uploading (`channels.list`)

It never reads anything about other people: viewers, commenters or other channels.

## What data it handles
- **My videos.** The video files I made, plus the titles and descriptions I wrote. After an upload, it saves the video ID, date and title in `uploads.json` in this repo so it doesn't upload the same video twice.
- **My login.** The OAuth client ID, client secret and refresh token are stored as encrypted GitHub secrets. They're never in the code or the logs. Each run swaps the refresh token for a short-lived access token, uses it for the two calls above, and throws it away when the run ends.

It doesn't collect, sell or share personal data, and it doesn't use cookies, analytics, ads or tracking.

## Turning it off
I can remove its access at any time in my Google Account under Security > Your connections to third-party apps & services (https://myaccount.google.com/connections), or by deleting the `YT_` secrets in this repo's settings. After that it can't reach YouTube at all.

## Google and YouTube
This tool uses the YouTube API Services and follows the YouTube API Services Terms of Service (https://developers.google.com/youtube/terms/api-services-terms-of-service). The YouTube Terms of Service apply to what it uploads (https://www.youtube.com/t/terms). Google's handling of data is covered by the Google Privacy Policy (https://policies.google.com/privacy).

## Contact
pandananoblock@gmail.com

See also the [terms of service](TERMS.md).
