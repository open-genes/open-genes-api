#!/bin/sh
TAG=$1
IMAGE=$TAG
[ "$IMAGE" = "" ] || IMAGE=":$IMAGE"
IMAGE="opengenes/backend$IMAGE"

BUILD=`git log HEAD --pretty=oneline --relative .| wc -l`
REVISION=`git rev-parse --short HEAD`
DATE=`date +%Y-%m-%d`
BRANCH=`git rev-parse --abbrev-ref HEAD`
echo "build=\"$BUILD\"\nrevision=\"$REVISION\"\ndate=\"$DATE\"\nbranch=\"$BRANCH\"" >VERSION
echo VERSION file written with build $BUILD revision $REVISION date $DATE branch $BRANCH
echo image $IMAGE

[ -f .env ] || cat /dev/null >.env
docker build -t $IMAGE .
