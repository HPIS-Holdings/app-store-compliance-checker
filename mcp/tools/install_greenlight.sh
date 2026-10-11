#!/usr/bin/env sh
# Install the pinned Greenlight release binary (MIT, https://github.com/RevylAI/greenlight) and verify its checksum.
# Only the offline `preflight --format json` command is used by the checker; nothing is uploaded.
set -eu
VER=0.2.0
OS=$(uname -s | tr A-Z a-z); ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64;; aarch64|arm64) ARCH=arm64;; esac
case "$OS-$ARCH" in
  linux-amd64)  SHA=1e075a588a3b7968de903e53d904cabc983904dadb76906cb5aa149acf07dfff;;
  linux-arm64)  SHA=66a2a1b8066bf468d4e352fa97492022d3596d69f45d6aa0b84c26aedb332d80;;
  darwin-amd64) SHA=f609cd2b8b810131d46ac231b6b7d124e9f22ab3ca13c646370c5d334ee36920;;
  darwin-arm64) SHA=4ccba1ab1608f80f9a89e7a7d092937116a63273ac9be9310ec95b696de43b5b;;
  *) echo "unsupported platform $OS-$ARCH" >&2; exit 2;;
esac
DEST=${GREENLIGHT_DIR:-$HOME/.local/share/mobile-compliance/greenlight-$VER}
TGZ=greenlight_${VER}_${OS}_${ARCH}.tar.gz
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
curl -fsSL -o "$TMP/$TGZ" "https://github.com/RevylAI/greenlight/releases/download/v$VER/$TGZ"
GOT=$( (sha256sum "$TMP/$TGZ" 2>/dev/null || shasum -a 256 "$TMP/$TGZ") | cut -d' ' -f1)
[ "$GOT" = "$SHA" ] || { echo "checksum mismatch: $GOT != $SHA" >&2; exit 3; }
mkdir -p "$DEST" && tar -xzf "$TMP/$TGZ" -C "$DEST" greenlight LICENSE && chmod +x "$DEST/greenlight"
"$DEST/greenlight" --version
