[![Build Status](https://travis-ci.org/bpicolo/adjure.svg?branch=master)](https://travis-ci.org/bpicolo/adjure)
# adjure
Adjure is a simple microservice for Two-Factor authentication. It provides endpoints for user provisioning, authorization, and generating relevant QR-codes to scan with Duo Security or Google Authenticator.

It handles a few of the quirks properly, e.g. despite the standard claiming support for SHA256, Google Authenticator doesn't actually support it.

For specifics (for now), hit up the code. There isn't too much to it :)

## Using adjure
make run
