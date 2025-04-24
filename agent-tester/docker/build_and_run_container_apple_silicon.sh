#!/bin/bash
# TODO: Docker entrypoint script

docker build -t agent-tester --platform linux/amd64 -f Dockerfile .

docker run --rm -it \
  --name agent-tester-container \
  -v "$(pwd)/..":/workspace \
  -w /workspace \
  --platform linux/amd64 \
  agent-tester bash
