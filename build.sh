
BUILD=`git log HEAD --pretty=oneline --relative .| wc -l`
REVISION=`git rev-parse --short HEAD`
DATE=`git rev-list --date=short --pretty=%cd HEAD |sed -n 2p`
echo "build=\"$BUILD\"\nrevision=\"$REVISION\"\ndate=\"$DATE\"" >VERSION
echo VERSION file written with build $BUILD revision $REVISION date $DATE

[ -f .env ] || cat /dev/null >.env
docker build -t opengenes/api .
