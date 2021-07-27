#!/usr/bin/env bash

set -e

pushd "${0%/*}"

./lint-check.sh && ./code-coverage.sh

return_code=$?

popd

exit ${return_code}