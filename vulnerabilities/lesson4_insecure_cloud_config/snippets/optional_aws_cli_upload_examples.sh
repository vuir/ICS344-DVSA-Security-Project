#!/usr/bin/env bash
# Lesson 4 - Optional AWS CLI upload examples
# Replace the bucket name and prefix with your own authorized lab values before running.

BUCKET="dvsa-recipts-bucket"
PREFIX="2026/04/27"

# Before-fix malformed upload test
aws s3 cp ../payloads/test.raw "s3://$BUCKET/$PREFIX/test.raw"

# Before-fix valid pattern test
aws s3 cp ../payloads/12345_abcde.raw "s3://$BUCKET/$PREFIX/12345_abcde.raw"

# After-fix malformed upload test
aws s3 cp ../payloads/badtest.raw "s3://$BUCKET/$PREFIX/badtest.raw"

# After-fix valid pattern test
aws s3 cp ../payloads/6789_abcde.raw "s3://$BUCKET/$PREFIX/6789_abcde.raw"
