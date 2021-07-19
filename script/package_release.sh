#!/bin/bash
set -x
PROJECT=ChatPlaysRTS
version=$1
zipfile=$PROJECT-$version.zip

if ! [ -n "$version" ]; then
	echo "Usage: $(basename $0) version" 1>&2
	exit 1
fi

mkdir -p .tmp/$PROJECT
files=$(git ls-tree -r HEAD --name-only | grep -v "^\.gitignore$")
rsync -R $files .tmp/$PROJECT
pushd .tmp
zip -r $zipfile $PROJECT
mv $zipfile ../
popd
rm -rf .tmp
