#!/bin/bash

echo "=== Updating system ==="
sudo apt update -y

echo "=== Installing requirements ==="
sudo apt install -y ca-certificates curl

echo "=== Creating keyring directory ==="
sudo install -m 0755 -d /etc/apt/keyrings

echo "=== Downloading Docker GPG key ==="
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

echo "=== Setting permissions for key ==="
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "=== Adding Docker repository ==="
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

echo "=== Updating and ready for Docker installation ==="
sudo apt update -y

echo "Done! You can now install Docker using:"
echo "  sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker
echo "Done! installation of Docker Completed"
