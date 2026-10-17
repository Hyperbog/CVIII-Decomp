#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec ./cviii-jp-native-demo --assets "$(pwd)/assets" "$@"
