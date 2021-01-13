#!/usr/bin/env bash

pushd $1 > /dev/null

if [ $(ls -1 *.mp3 | wc -l) -eq 0 ]; then
  echo no mp3 files found no need to move files
  exit 0
fi

# create needed directories
while IFS= read -r line; do
  mkdir -p "$2/$line"
done < <(eyeD3 -P display --pattern '%a%/%A%' *.mp3 | sort | uniq)

# move files to media library folder
for f in *.mp3; do
  dest="$2/$(eyeD3 -P display --pattern '%a%/%A%/$num(%n%,2) %t%.mp3' "$f")"
  mv "$f" "$dest"
done

popd > /dev/null
