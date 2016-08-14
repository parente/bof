# BoF App

Web app to aid off-the-cuff planning of Birds of a Feather (BoF) sessions at a venue

## Development

```
cd bof
pip install -r requirements.txt
FLASK_APP=bof/__init__.py FLASK_DEBUG=1 flask run
```

## Deploy to Cloud Foundry

Create a manifest.yml that inherits from base-manifest.yml:

```
applications:
- name: bof
  host: bof
  env:
    GITHUB_CLIENT_ID: 'replace with GitHub OAuth client ID'
    GITHUB_CLIENT_SECRET: 'replace with GitHub OAuth secret'
    SECRET_KEY: 'replace with a random string'
    SQLALCHEMY_DATABASE_URI: 'postgresql+pg8000://username:password@host:port/database'
```

Push it.

```
cf push
```

## Use Cases

### MVP

* [X] As the first user, I want to see more than an empty page
* [X] As a user, I want to see what flocks are planned, where they are meeting at the venue, when, and with whom
* [X] As a user, I want to authenticate with GitHub in order to perform other BoF actions
* [X] As an authenticated user, I want to propose a flock
* [X] As an authenticated user, I want to join a flock
* [X] As an authenticated user, I want to leave a flock
* [X] As an authenticated user, I want to edit my flock details
* [X] As an authenticated user, I need a busy indicator while my actions are in flight
* [X] As an admin, I want to deploy the app
* [ ] As an admin, I want to seed suggested flock locations
* [ ] As an admin, I want control over content
* [ ] As an admin, I want control over users accounts

### Bonus

* As a user, I want to see flock updates without refreshing
* As a user, I want to authenticate with a service other than GitHub
* As an authenticated user, I want to join my flock with another
* As an authenticated user, I want to spruce up my flock card with an image

### Nits

* Format the bird list on the cards
* Highlight name field when there's a duplicate flock name error
* Enter key should submit form
* Continue showing last fetched list of flocks when refresh fails
* favicon

### Questions

* What happens on transaction conflicts (e.g., update a flock while someone joins)?
