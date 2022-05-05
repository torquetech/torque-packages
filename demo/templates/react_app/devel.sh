#!/bin/bash

export PORT=80

set -x

npm install || exit 1
npm start || exit 1
