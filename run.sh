#!/bin/bash

cd "$(dirname "$0")"

if command -v python3 &>/dev/null; then
    python3 cf-dns-update.py
else
    python cf-dns-update.py
fi
