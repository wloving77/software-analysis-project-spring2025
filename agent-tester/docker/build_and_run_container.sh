#!/bin/bash
# TODO: Docker entrypoint script

docker build -t agent-tester -f Dockerfile .

docker run --rm -it \
  --name agent-tester-container \
  -v "$(pwd)/..":/workspace \
  -w /workspace \
  agent-tester bash
