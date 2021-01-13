#!/usr/bin/env bash

if ! command -v xmms2 &> /dev/null; then
  cat > all_album.txt <<EOF
Adventskalender 2020
Album Name
Dummy Album 2
Dummy Album 3
Dummy: Album 1
EOF
else
  medialib_path=$(xmms2 server config medialib.path | awk 'BEGIN { FS="=" }; { print $2 }')
  sqlite3 $medialib_path > all_album.txt <<EOF
select distinct value from Media where key = 'album' order by 1;
EOF
fi

grep -h -A 1 -E "(album|advent)" $1/* | grep -v -- "--" | grep -v album | grep -v advent | sed s/\\\\:/:/ | sed s/\"//g | sort > assigned_album.txt

comm -23 all_album.txt assigned_album.txt
rm all_album.txt assigned_album.txt
