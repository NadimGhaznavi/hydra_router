#!/bin/bash 
#

SRC=hydra_router
DEST=/opt/dev/hydra_router/hydra_venv/lib/python3.11/site-packages/hydra_router

rm -rf $DEST
mkdir $DEST
rsync -avr --delete $SRC/* $DEST
