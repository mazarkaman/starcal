for old in *.svg ; do
    new="$(echo "$old" | sed -e 's/svg$/new.svg/')"
    rsvg-convert "$old" -w 320 -h 320 -f svg -o "$new"
    cp "$new" "$old"
    rm "$new"
done
