# iiifCollectionBrowse

v0.1.0

[![Build Status](https://travis-ci.org/uchicago-library/iiifcollectionbrowse.svg?branch=master)](https://travis-ci.org/uchicago-library/iiifcollectionbrowse) [![Coverage Status](https://coveralls.io/repos/github/uchicago-library/iiifcollectionbrowse/badge.svg?branch=master)](https://coveralls.io/github/uchicago-library/iiifcollectionbrowse?branch=master)

Browses IIIF collections

## Quickstart

### Dockerized

```
$ git clone https://github.com/uchicago-library/iiifcollectionbrowse
$ docker build . -t iiifcollectionbrowse
$ docker run -p 5000:80 -v ../iiifcollectionbrowse:/code iiifcollectionbrowse
```
Now open http://localhost:5000/ in your web browser.

### Old School

#### Prerequisites

- python3.5
- pip

```
$ git clone https://github.com/uchicago-library/iiifcollectionbrowse
$ cd iiifcollectionbrowse
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install requirements.txt
$ pip install requirements_dev.txt
$ IIIFCOLLBROWSE_DEFAULT_URL=https://iiif-collection.lib.uchicago.edu/top.json ./debug.sh
```

#### A quick note about the two different requirements text files: 

requirements.txt file is [the best practice](https://pip.readthedocs.io/en/1.1/requirements.html) for sharing the third-party libraries required for an application to run.

requirements_dev.txt is the list of third party libraries in order to run all the tests that a good developer ought to be running every time she commits.

## UChicago Internal Project Information

### Project Roadmap

[Project task items](https://docs.google.com/spreadsheets/d/12tCbNDxhcFOGfHpSguOFPhIOFsFVlb3OLlZJK9wUPk4/edit?usp=sharing)

### Internal Documentation

[Getting up and running with Docker](https://github.com/uchicago-library/Library_Digital_Repository_Documentation/wiki/crash-course-docker)

## Authors
- Tyler Danstrom (tdansrom@uchicago.edu) (current backend developer; responsible for Flask coding and unit tests)
- Brian Balsamo <brian@brianbalsamo.com> (backend developer; creator of the project)
- Kathy Zadrozny (kzadrozny@uchicago.edu) (frontend developer; responsible for SASS/CSS, Javascript, HTML and all accessibility-related changes)
