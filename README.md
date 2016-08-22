# BoF App

A web app to aid off-the-cuff planning of Birds of a Feather (BoF) sessions at a venue

## Run for Development

NOTE: Not using conda/conda-forge at the moment because of SSL verification problems when communicating with GitHub to fetch user data. (Bad certificates package?)

```
pip install -r requirements.txt
export GITHUB_CONSUMER_KEY='your app github key'
export GITHUB_CONSUMER_SECRET='your app github secret'
python -m bof.admin data examples
FLASK_APP=bof/__init__.py FLASK_DEBUG=1 flask run
```

## Deploy to Cloud Foundry

Create a `dev-manifest.yml` and/or `prod-manifest.yml` that inherits from base-manifest.yml:

```
---
inherit: base-manifest.yml
applications:
- name: bof
  host: bof
  env:
    GITHUB_CONSUMER_KEY: 'replace with GitHub OAuth client ID'
    GITHUB_CONSUMER_SECRET: 'replace with GitHub OAuth secret'
    SECRET_KEY: 'replace with a random string'
    SQLALCHEMY_DATABASE_URI: 'postgresql+pg8000://username:password@host:port/database'
    SQLALCHEMY_POOL_SIZE: 1     # per worker
```

Push it.

```
cf push -f dev-manifest.yml
```

For zero-downtime deploys, get https://github.com/contraband/autopilot, make sure you have twice the app allocated resources available, and then run:

```
cf zero-downtime-push bof -f dev-manifest.yml
```

If the zero-downtime deploy goes bad, just use `cf delete` to remove the botched app and `cf rename` to rename the venerable instance back to the main instance.

## Administer the Database

Set `SQLALCHEMY_DATABASE_URI` in your environment. Then run:

```
python -m bof.admin --help
```
