#!/bin/sh
TAG=$1
IMAGE=$TAG
[ "$IMAGE" = "" ] || IMAGE=":$IMAGE"
IMAGE="opengenes/api$IMAGE"

BUILD=`git log HEAD --pretty=oneline --relative .| wc -l`
REVISION=`git rev-parse --short HEAD`
DATE=`git rev-list --date=short --pretty=%cd HEAD |sed -n 2p`
BRANCH=`git rev-parse --abbrev-ref HEAD`
echo "build=\"$BUILD\"\nrevision=\"$REVISION\"\ndate=\"$DATE\"\nbranch=\"$BRANCH\"" >VERSION
echo VERSION file written with build $BUILD revision $REVISION date $DATE
echo image $IMAGE

[ -f .env ] || cat /dev/null >.env
docker build -t $IMAGE .
