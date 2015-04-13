#!/bin/sh
# (c) 2015, Jaguar Land Rover, Rudolf J Streif
# Create Docker images for different base OS
# We currently support Fedora and Ubuntu only.

test -z "$1" && echo "No target OS specified [fedora, ubuntu]." && exit 1

OS=$1
OS=${OS,,}

test ! -e "Dockerfile.$OS" && echo "Dockerfile.$OS does not exist." && exit 1

test -e "Dockerfile" && rm "Dockerfile"
ln -s "Dockerfile".$OS "Dockerfile"
docker build --no-cache -t "dc-rvitools-"$OS .
rm "Dockerfile"

