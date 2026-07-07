#!/bin/bash

check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        echo -n "{\"name\":\"$1\",\"installed\":true,\"path\":\"$(command -v "$1")\"}"
    else
        echo -n "{\"name\":\"$1\",\"installed\":false,\"path\":\"\"}"
    fi
}

echo -n "{"
echo -n "\"simg2img\":"$(check_cmd simg2img)","
echo -n "\"img2simg\":"$(check_cmd img2simg)","
echo -n "\"lpunpack\":"$(check_cmd lpunpack)","
echo -n "\"lpmake\":"$(check_cmd lpmake)","
echo -n "\"lpdump\":"$(check_cmd lpdump)
echo -n "}"
