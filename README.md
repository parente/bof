# BoF App

Web app to aid off-the-cuff planning of Birds of a Feather (BoF) sessions at a venue

## Use Cases

### MVP

* [X] As the first user, I want to see more than an empty page
* [X] As a user, I want to see what flocks are planned, where they are meeting at the venue, when, and with whom
* [X] As a user, I want to authenticate with GitHub in order to perform other BoF actions
* [X] As an authenticated user, I want to propose a flock
* [X] As an authenticated user, I want to join a flock
* [X] As an authenticated user, I want to leave a flock
* [X] As an authenticated user, I want to edit my flock details
* [ ] As an admin, I want to seed suggested flock locations
* [ ] As an admin, I want to deploy the app
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

### Questions

* What happens on transaction conflicts (e.g., update a flock while someone joins)?
