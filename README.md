Requirements
============

1. Docker 1.13.0+
1. Docker-compose 1.10.0+ (supporting compose file version 3.0).

Setup
=====

1. `docker-compose up`
1. Navigate to http://127.0.0.1:1000

Other useful commands
=====================

* Run automated tests (most of them are named, but not implemented, as those implemented is enough for demonstration): `docker run issuetracker_web python /code/manage.py test`

* Populate the DB with some data for manual testing (`docker-compose up` should be still running): `docker exec issuetracker_web_1 python /code/manage.py loaddata /code/issuetracker/fixtures/manual_testing.yaml`

    Superuser login: admin/adminadmin
    Staff login: staff/staffstaff

* Remove Docker containers, volumes, and used local images: `docker-compose down --volumes --rmi local`
