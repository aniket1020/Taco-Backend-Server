## Setup:
- Add `.env` file containing `AUTH_KEY`
- Add the `participant-sa-15-ghc-011.json`

## SSL Config steps:
- Enable http traffic on the GCP VM using Network tags.
- Use a free SSL certificate provider service to generate free SSL certificates to enable https traffic.
-- You will have to serve an authentication text-file on a specific url endpoint, as part of generating the SSL certificates. This can be done using nginx or Flask endpoint using on http server url.
-- Once the certificates are generated add them to the root folder using the same naming scheme used in `startup.sh`.

## Starting server
- Run `startup.sh &`. This will be a daemon process. To terminate this use `top` or install and use `htop`

## Usage
- Use the `AUTH_KEY` in POST request headers with key `Authorization` 
