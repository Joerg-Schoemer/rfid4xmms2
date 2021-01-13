#!/usr/bin/env bash

if ! command -v xmms2 &> /dev/null; then
  echo '{ "status": "Playing", "artist": "Katharina Westerhoff", "album": "Adventskalender 2020", "title": "Tag 11", "playtime": "00:'$(printf "%02d" $(($RANDOM % 60)))'", "duration": "02:02" }'
else
  xmms2 current -f '{ "status": "${playback_status}", "artist": "${artist}", "album": "${album}", "title": "${title}", "playtime": "${playtime}", "duration": "${duration}" }'
fi
