FROM --platform=linux/amd64 debian:bookworm
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    live-build debootstrap squashfs-tools xorriso isolinux syslinux-common syslinux-utils \
    grub-pc-bin grub-efi-amd64-bin grub-efi-ia32-bin mtools dosfstools ca-certificates git curl \
    imagemagick gnupg rsync xz-utils zsync \
 && rm -rf /var/lib/apt/lists/*
