docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/rickhqh/hotmail-checker . --push
##docker build -t hotmail-checker .  --load &&
docker run --name hotmail-checker -d \
  -v /Users/rick/python/hotmail-checker/config:/hotmail-checker/config \
  -v /Users/rick/python/hotmail-checker/out:/hotmail-checker/out \
  -v /Users/rick/python/hotmail-checker/emails:/hotmail-checker/emails \
  ghcr.io/rickhqh/hotmail-checker:latest

#docker run --name hotmail-checker -d \
#   -v /root/hotmail-checker/config:/hotmail-checker/config \
#   -v /root/hotmail-checker/emails:/hotmail-checker/emails \
#   -v /root/hotmail-checker/out:/hotmail-checker/out \
#   ghcr.io/rickhqh/hotmail-checker:latest
