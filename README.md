# Repository Boilerplate

A boilerplate that can be used as a template for quickly setting up a repository for a web application with the following stacks:

1. __Backend__ in [_Django_](https://www.djangoproject.com/) & [_Django Restframework_](https://www.django-rest-framework.org/)
2. __Frontend__ in [_ReactJS_](https://react.dev/)
3. __Application__ in [_React Native_](https://reactnative.dev/)
4. __Stable Storage__ in [_PostgreSQL_](https://www.postgresql.org/)
5. __Warehousing/Lake__ in [_MongoDB_](https://www.mongodb.com/)
6. __In-Memory Datasource/ Caching (_Frontend Only_)__ in [_Redis_](https://redis.io/)

## Setup

The setup procedures are defined as follows

### Pre-Requisites

1. __Console__: _[BASH](https://www.gnu.org/software/bash/)_
    - _[GitBASH](https://git-scm.com/downloads)_ for __Windows__
2. __[Python](https://www.python.org/)__ _v3.9_
3. __[NPM](https://www.npmjs.com/)__ _v9.6_
4. __[React-JS](https://legacy.reactjs.org/)__ _v9.6_
5. __[React-Native](https://reactnative.dev/)__ _v9.6_
6. __[PostreSQL](https://www.postgresql.org/)__ & __[PGAdmin](https://www.pgadmin.org/)__
7. __[MongoDB](https://www.mongodb.com/)__ & __[MongoDB Compass](https://www.mongodb.com/products/compass)__
8. __[Redis](https://redis.io/)__
9. __[Crontab](https://man7.org/linux/man-pages/man5/crontab.5.html)__

#### Repository Procurement

`git clone https://<personalAccessToken>@github.com/Arkiralor/ProjectBoilerplate.git`

#### How to use the Boilerplate

1. Run the procurement command shown above.
2. Delete the `.git` directory from the cloned repository.
3. Rename the repository-directory to one that is more appropriate for the purpose of the codebase.
4. Run `git init` from inside the repository-directory (_level-0_) to initiate a new repository.
5. Code away...!

#### Backend Setup

See [`backend/readme.md`](https://github.com/Arkiralor/ProjectBoilerplate/blob/master/backend/README.md)

#### Frontend Setup

See `frontend/readme.md`

#### Application Setup

See `app/readme.md`

#### PostgreSQL/PGADmin Setup

Details [here](https://www.postgresql.org/docs/current/tutorial-install.html).

#### MongoDB/Compass Setup

Details [here](https://www.mongodb.com/docs/manual/administration/install-community/).

#### Redis Setup

Details [here](https://redis.io/docs/getting-started/installation/).

## Documentation

Documentation can be viewed in each Tier-1 directory's `readme.md` file.
