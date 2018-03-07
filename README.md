# iiifCollectionBrowse

v0.0.1

[![Build Status](https://travis-ci.org/uchicago-library/iiifcollectionbrowse.svg?branch=master)](https://travis-ci.org/uchicago-library/iiifcollectionbrowse) [![Coverage Status](https://coveralls.io/repos/github/uchicago-library/iiifcollectionbrowse/badge.svg?branch=master)](https://coveralls.io/github/uchicago-library/iiifcollectionbrowse?branch=master)

Browses IIIF collections

# Quickstart

```
$ git clone https://github.com/uchicago-library/iiifcollectionbrowse
$ docker build . -t iiifcollectionbrowse
$ docker run -p 5000:80 -v ../iiifcollecitionbrowse:/code iiifcollectionbrowse
```

Now open http://localhost:5000/ in your web browser.

# Author
Brian Balsamo <brian@brianbalsamo.com>
