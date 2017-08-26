#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install tor
sudo echo "MaxCircuitDirtiness 10" >> /etc/tor/torrc

echo "\t\tInstalling Anaconda"
wget -S -T 10 -t 5 https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh -O $HOME/anaconda.sh
sudo bash $HOME/anaconda.sh -b -p $HOME/anaconda
sudo rm $HOME/anaconda.sh
export PATH=$HOME/anaconda/bin:$PATH
echo "export PATH=$HOME/anaconda/bin:$PATH" >> $HOME/.bashrc
# pip install pysocks
pip install pymongo
pip install fake_useragent


echo "export MONGO_USER1=root" >> $HOME/.bashrc
echo "export MONGO_USER1_PW=123456" >> $HOME/.bashrc
echo "export MONGO_USER2=fragrance" >> $HOME/.bashrc
echo "export MONGO_USER2_PW=fragrance" >> $HOME/.bashrc
