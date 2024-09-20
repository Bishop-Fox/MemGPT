export MEMGPT_VERSION=$(memgpt version)
echo $MEMGPT_VERSION
#docker buildx build --platform=linux/arm64 --build-arg MEMGPT_ENVIRONMENT=RELEASE -t memgpt/memgpt-server:${MEMGPT_VERSION} . --load
