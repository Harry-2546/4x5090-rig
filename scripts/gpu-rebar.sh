#!/bin/bash
# Grow RTX 5090 BAR1 to 32G and re-enumerate the PEX88096 tree, then load nvidia.
# BIOS Re-Size BAR stays off (4 x 32G BARs hang POST); needs pci=nocrs so the
# 192G bridge window can go above the BIOS 64-bit window.
set -u
ROOT_PORT=0000:00:01.0
GPU_ID=10de:2b85
BAR1_SIZE=$((32 << 30))

gpus() { lspci -D -d "$GPU_ID" | cut -d" " -f1; }
bar1() { sed -n 2p "/sys/bus/pci/devices/$1/resource"; }

# If something loaded nvidia first (e.g. nvidia-cdi-refresh.service from
# nvidia-container-toolkit), it binds the GPUs during rescan and resets
# ReBAR to 256M. Unload it before touching the BARs.
if grep -q "^nvidia " /proc/modules; then
	echo "gpu-rebar: nvidia already loaded, unloading first"
	modprobe -r nvidia_drm nvidia_modeset nvidia_uvm nvidia ||
		echo "gpu-rebar: unload failed (GPU in use?)"
fi

need=0
for d in $(gpus); do
	ctrl=0x$(setpci -s "$d" ECAP15+8.l) || continue
	if [ $(( (ctrl >> 8) & 0x3f )) -ne 15 ]; then
		setpci -s "$d" COMMAND=0000:0002
		setpci -s "$d" ECAP15+8.l=$(printf %08x $(( (ctrl & ~0x3f00) | (15 << 8) )))
		need=1
	fi
	read -r s _ <<<"$(bar1 "$d")"
	[ $((s)) -eq 0 ] && need=1
done

if [ $need -eq 1 ]; then
	echo 1 > "/sys/bus/pci/devices/$ROOT_PORT/remove"
	sleep 2
	echo 1 > /sys/bus/pci/rescan
	sleep 3
fi

n=0; ok=0
for d in $(gpus); do
	n=$((n + 1))
	read -r s e _ <<<"$(bar1 "$d")"
	[ $((s)) -ne 0 ] && [ $((e - s + 1)) -eq $BAR1_SIZE ] && ok=$((ok + 1))
done
echo "gpu-rebar: $ok/$n GPUs have a 32G BAR1"

modprobe -a nvidia nvidia_uvm nvidia_modeset nvidia_drm
[ $ok -eq $n ] && [ $n -gt 0 ]
