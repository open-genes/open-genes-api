
echo build=`git log HEAD --pretty=oneline --relative .| wc -l` "\n"revision=\"`git rev-parse --short HEAD`\""\n"date=`git rev-list --date=short --pretty=%cd HEAD |sed -n 2p` >VERSION

[ -f .env ] || cat /dev/null >.env
docker build -t opengenes/api .
