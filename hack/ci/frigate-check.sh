#!/usr/bin/env bash

# Useful script to run in the CI to check if the generated README.md is up to date

set -e

python -m pip install -r requirements-dev.txt
tempFile=$(mktemp)
frigate gen --no-credits -o markdown deployments/kubernetes/helm/k8s-tunnel-controller > ${tempFile}
diff -u deployments/kubernetes/helm/k8s-tunnel-controller/README.md ${tempFile}
