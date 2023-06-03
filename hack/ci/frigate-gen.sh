#!/usr/bin/env bash

# Useful script to generate the chart README.md

set -e

python -m pip install -r requirements-dev.txt
frigate gen --no-credits -o markdown deployments/kubernetes/helm/k8s-tunnel-controller > deployments/kubernetes/helm/k8s-tunnel-controller/README.md