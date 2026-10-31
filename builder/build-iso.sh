#!/usr/bin/env bash
# Runs INSIDE the container. Builds in /build (native fs; live-build breaks on macOS bind mounts).
set -euo pipefail
rm -rf /build && mkdir /build && cd /build
ARCH=${ARCH:-amd64}
cp -a /src/config .
# Per-architecture package lists and boot menu label
for a in amd64 arm64; do [ "$a" = "$ARCH" ] || rm -f "config/package-lists/$a-only.list.chroot"; done
sed -i "s/Endy Linux (amd64)/Endy Linux ($ARCH)/" config/bootloaders/grub-pc/grub.cfg
if [ "$ARCH" = amd64 ]; then BOOTLOADERS=syslinux,grub-efi; else BOOTLOADERS=grub-efi; fi
lb config \
  --distribution bookworm --architectures $ARCH \
  --archive-areas "main contrib non-free non-free-firmware" \
  --parent-archive-areas "main contrib non-free non-free-firmware" \
  --debian-installer none \
  --binary-images iso-hybrid \
  --bootloaders "$BOOTLOADERS" \
  --bootappend-live "boot=live components quiet splash username=macbook hostname=macbookos locales=en_US.UTF-8 keyboard-layouts=us keyboard-variants=intl keyboard-options=altwin:ctrl_win timezone=America/Sao_Paulo" \
  --zsync false --iso-application "MacBookOS" --iso-volume "MacBookOS" \
  --apt-recommends false --firmware-chroot true \
  --compression xz --memtest none --win32-loader false \
  --linux-flavours $ARCH --security true --updates true
# Persist live-build's bootstrap + package cache across runs (docker volume mounted at /cache)
mkdir -p /cache && rm -rf /build/cache && ln -s /cache /build/cache
lb build 2>&1 | tee /output/build.log || true
# Keep the ISO even if a late optional step (e.g. zsync) fails
ls ./*.iso >/dev/null 2>&1 || { echo 'no ISO produced'; exit 1; }
mv -v ./*.iso /output/MacBookOS-$ARCH.iso
( cd /output && sha256sum MacBookOS-$ARCH.iso > MacBookOS-$ARCH.iso.sha256 )
