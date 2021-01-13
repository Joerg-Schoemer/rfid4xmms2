#!/usr/bin/env bash

if [[ ! "$1" =~ ^(play|stop|pause|next|prev|toggle|clear|add.*)$ ]]; then
  echo Invalid argument 1>&2
  exit 1
fi

if ! command -v xmms2 &> /dev/null; then
  echo "xmms2 $1"
  exit 0
fi

xmms2 $1
