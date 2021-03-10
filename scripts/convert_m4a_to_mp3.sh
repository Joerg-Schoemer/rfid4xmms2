#!/usr/bin/env bash

pushd $1 > /dev/null

if [[ $(ls -1 *.m4a 2> /dev/null | wc -l) -eq 0 ]]; then
  echo no need to convert any m4a file
  exit
fi

if ! command -v parallel &> /dev/null; then
  for f in *.m4a; do
    ffmpeg -v 5 -y -i "$f" -codec:a libmp3lame -b:a 128k "$(basename "$f" .m4a).mp3"
  done
else
(
# build a list of commands to convert the m4a and execute it parallel
  for f in *.m4a; do
    echo ffmpeg -v 5 -y -i "\"$f\"" -codec:a libmp3lame -b:a 128k "\"$(basename "$f" .m4a).mp3\""
  done
) | parallel
fi

# remove all m4a files
rm *.m4a

popd > /dev/null
