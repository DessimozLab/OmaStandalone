#!/bin/sh
# Installs the latest OMA standalone release from GitHub into the standalone
# folder of the OMA browser. The release workflow attaches the files to the
# GitHub release; this script is meant to run from cron, e.g. hourly:
#
#   17 * * * * /path/to/sync-release.sh /pub/projects/cbrg-oma-browser/standalone
#
# It does nothing if the latest release is already installed or if its files
# are not attached yet.

set -eu

if [ $# -ne 1 ] ; then
    echo "usage: $0 <standalone web folder>" >&2
    exit 1
fi
webpath=$1
repo=DessimozLab/OmaStandalone

# drafts and pre-releases are never "latest"
tag=$(curl -fsSL "https://api.github.com/repos/$repo/releases/latest" \
      | sed -n 's/^ *"tag_name": *"\([^"]*\)".*/\1/p')
if [ -z "$tag" ] ; then
    echo "could not determine latest release of $repo" >&2
    exit 1
fi

# OMA.latest.tgz is switched last, so it marks a complete installation
if [ "$(readlink "$webpath/OMA.latest.tgz" 2>/dev/null)" = "OMA.$tag.tgz" ] ; then
    exit 0
fi

tmp=$(mktemp -d "$webpath/.sync.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
base="https://github.com/$repo/releases/download/$tag"

# SHA256SUMS is attached last; without it the release is not ready yet
if ! curl -fsSL -o "$tmp/SHA256SUMS" "$base/SHA256SUMS" 2>/dev/null ; then
    exit 0
fi
for f in "OMA.$tag.tgz" "OMA.$tag-website.tar.gz" ; do
    curl -fsSL -o "$tmp/$f" "$base/$f"
done
(cd "$tmp" && sha256sum --quiet -c SHA256SUMS)

mkdir "$tmp/website"
tar -xzf "$tmp/OMA.$tag-website.tar.gz" -C "$tmp/website"
cp -r "$tmp/website/." "$webpath/"
mv "$tmp/OMA.$tag.tgz" "$webpath/"
ln -s "OMA.$tag.tgz" "$tmp/OMA.latest.tgz"
mv -f "$tmp/OMA.latest.tgz" "$webpath/OMA.latest.tgz"

echo "installed OMA standalone $tag"
