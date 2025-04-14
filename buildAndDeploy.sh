#!/bin/bash

# One-time setup for multi-architecture build (only runs if needed)
if ! sudo docker buildx inspect multiarch-builder &>/dev/null; then
  echo "🔧 Setting up buildx for multi-arch support..."
  sudo docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
  sudo docker buildx create --use --name multiarch-builder
else
  echo "✅ buildx builder already exists. Using 'multiarch-builder'."
  sudo docker buildx use multiarch-builder
fi

# Make sure builder is bootstrapped
sudo docker buildx inspect --bootstrap

# Multi-arch build and push
echo "🚀 Building and pushing multi-arch image..."
sudo docker buildx build --platform linux/amd64,linux/arm64 -t eliteabhi/camera-interface:latest . --push

# Start container
echo "🟢 Starting services with docker compose..."
sudo docker compose up -d

