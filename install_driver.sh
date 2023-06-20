#!/bin/bash

# SourceL https://github.com/waywardgeek/infnoise/tree/master/software
wget -O 13-37.org-code.asc https://13-37.org/files/pubkey.gpg
gpg --with-fingerprints 13-37.org-code.asc
gpg2 --import-options import-show --dry-run --import < 13-37.org-code.asc
sudo apt-key add 13-37.org-code.asc
echo "deb http://repo.13-37.org/ stable main" | sudo tee /etc/apt/sources.list.d/infnoise.list
sudo apt update
rm 13-37.org-code.asc
sudo apt install infnoise
