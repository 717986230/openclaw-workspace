# OpenClaw Skills Audit

Generated: 2026-04-15 10:24:00 +08:00

## Summary

- Total skills: 68
- Ready: 33
- Needs setup: 35
- Disabled: 0
- Blocked by allowlist: 0
- Windows-feasible missing skills: 32
- OS-blocked missing skills: 8

## Changes Applied

- Removed redundant junctions under `C:\Users\Administrator\.openclaw\skills` that pointed to `C:\Users\Administrator\.agents\skills`.
- Verified no `symlink-escape` warnings remain in `openclaw skills check`.
- Installed and verified high-value Windows-feasible CLIs that do not require credentials:
  - `gemini`
  - `openai-whisper`
  - `summarize`
  - `xurl`
- Added a local compatibility shim for `obsidian-cli` that delegates to the installed `obsidian` CLI.
- Re-ran `openclaw skills check` after remediation.
- Verified counts improved to `68 / 33 / 35 / 0 / 0`.

## Verified Ready Skills

- `agent-reach`
- `github`
- `gemini`
- `obsidian`
- `openai-whisper`
- `summarize`
- `xurl`

## Verified Needs Setup Skills

- `slack` -> missing `channels.slack`
- `opentwitter` -> missing `TWITTER_TOKEN`

## Environment Status

All targeted gateway environment variables were absent at process, user, and machine scope:

- `NOTION_API_KEY`
- `OPENAI_API_KEY`
- `TWITTER_TOKEN`
- `TRELLO_API_KEY`
- `TRELLO_TOKEN`
- `SHERPA_ONNX_RUNTIME_DIR`
- `SHERPA_ONNX_MODEL_DIR`
- `GOOGLE_PLACES_API_KEY`
- `ELEVENLABS_API_KEY`

## Config Gates Left Unchanged

These were intentionally not enabled because no live configuration or user intent was present:

- `channels.slack`
- `channels.bluebubbles`
- `plugins.entries.voice-call.enabled`

## Needs Setup: Config Only

- `bluebubbles` -> `channels.bluebubbles`
- `slack` -> `channels.slack`
- `voice-call` -> `plugins.entries.voice-call.enabled`

## Needs Setup: Env Only

- `notion` -> `NOTION_API_KEY`
- `openai-whisper-api` -> `OPENAI_API_KEY`
- `opentwitter` -> `TWITTER_TOKEN`
- `trello` -> `TRELLO_API_KEY`, `TRELLO_TOKEN`
- `sherpa-onnx-tts` -> `SHERPA_ONNX_RUNTIME_DIR`, `SHERPA_ONNX_MODEL_DIR`

## Needs Setup: Bin Plus Env

- `goplaces` -> binary `goplaces` and env `GOOGLE_PLACES_API_KEY`
- `sag` -> binary `sag` and env `ELEVENLABS_API_KEY`

## Needs Setup: Bin Only

- `1password` -> `op`
- `blogwatcher` -> `blogwatcher`
- `blucli` -> `blu`
- `camsnap` -> `camsnap`
- `eightctl` -> `eightctl`
- `gifgrep` -> `gifgrep`
- `gog` -> `gog`
- `himalaya` -> `himalaya`
- `mcporter` -> `mcporter`
- `nano-pdf` -> `nano-pdf`
- `openhue` -> `openhue`
- `oracle` -> `oracle`
- `ordercli` -> `ordercli`
- `songsee` -> `songsee`
- `sonoscli` -> `sonos`
- `spotify-player` -> any of `spogo` or `spotify_player`
- `wacli` -> `wacli`

## OS-Blocked On This Windows Host

- `apple-notes` -> requires `memo`, `darwin`
- `apple-reminders` -> requires `remindctl`, `darwin`
- `bear-notes` -> requires `grizzly`, `darwin`
- `imsg` -> requires `imsg`, `darwin`
- `model-usage` -> requires `codexbar`, `darwin`
- `peekaboo` -> requires `peekaboo`, `darwin`
- `things-mac` -> requires `things`, `darwin`
- `tmux` -> requires `tmux`, `darwin` or `linux`

## Deferred By Design

- No credentials were written because no valid secrets were present.
- No channel configs were added for Slack or BlueBubbles.
- No `voice-call` plugin entry was added because the plugin was not already configured.
- Remaining third-party CLI tools were deferred unless you explicitly want them on this host.
