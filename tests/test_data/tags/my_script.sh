#!/usr/bin/env bash

FILEPATH=$1

grep --count l "$FILEPATH"
