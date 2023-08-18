#!/bin/sh

if [ $# -lt 1 ]; then
  echo "Usage: $0 <tag>"
  exit 1
fi

tag=$1
changelogFile='CHANGELOG.md'

logOutput=$(git log $tag..HEAD --pretty=format:"- %s" --no-merges | sed 's/#//g')

echo "#Release v$tag" >> $changelogFile
echo "" >> $changelogFile
echo "$logOutput" >> $changelogFile

echo "Changelog has been updated and saved to $changelogFile"