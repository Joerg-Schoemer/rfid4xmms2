#!/usr/bin/env bash

if ! command -v xmms2 &> /dev/null; then
    echo "Dummy Album | Dummy Title 1"
    echo "Dummy Album | Dummy Title 2"
    echo "Dummy Album 1 | Dummy Title 1"
    exit
fi

xmms2 search -l album,title -o album,partofset,tracknr,title title:"*" | awk '{ $1=$1 };1' | tail -n +3 | head -n -1
