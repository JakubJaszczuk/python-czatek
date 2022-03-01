#!/bin/bash

rm -r ./src/proto/*
protoc proto/*.proto --python_out=src/
