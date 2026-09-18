#!/bin/bash
# Normalize CASE_DIR to absolute path so actors running inside MUSCLE3 instance directories can locate case assets
export CASE_DIR="$(cd "$CASE_DIR" && pwd)"

