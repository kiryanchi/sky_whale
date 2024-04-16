#!/bin/bash

poetry export -f requirements.txt > requirements.txt

docker compose up -d --build sky_whale