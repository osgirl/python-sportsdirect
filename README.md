python-sportsdirect
===================

Python client library for the Sports Direct Inc. XML Feeds.

Caveats
-------

This was written to support news applications for the 2015-2016 NFL season.  As a result, we've only implemented an API around the feeds we needed.  We'll continue to implement support for additional sports/league feeds as needed/time permits.

Installation
------------

pip install git+https://github.com/newsapps/python-sportsdirect.git

Examples
--------

### Get all NFL games

    >>> from sportsdirect.schedule import get_schedule
    >>> games = get_schedule('football', 'NFL')
    >>> print(games[0].home_team.name)
    Carolina

Tests
-----

To run the unit tests for this package, run:

    python setup.py test

Authors
-------

* Geoff Hing <geoffhing@gmail.com>
* Abe Epton

Changelog
---------

### 0.2

Parse venues information in NFL schedules.

### 0.1

Initial release.
