[![Build Status](https://travis-ci.org/ftiff/pymacad.svg?branch=master)](https://travis-ci.org/ftiff/pymacad)
[![codecov.io](https://codecov.io/github/ftiff/pymacad/coverage.svg?branch=master)](https://codecov.io/github/ftiff/pymacad?branch=master)

# pymacad

## Acknowledgments 

This python package is based on KerbMinder (http://github.com/pmbuko/KerbMinder). 

* [Peter Bukowinski](http://github.com/pmbuko), author of KerbMinder
* [Francois 'ftiff' Levaux-Tiffreau](http://github.com/ftiff), who extracted this package
* [Ben Toms](http://github.com/macmule), who gave ftiff the idea
* [Allister Banks](https://twitter.com/Sacrilicious/status/543451138239258624) for pointing out an effective dig command to test for domain reachability.

## pymacad.ad

I would suggest to use `from pymacad import ad` -- then call using ad.xxx

### Example
```python
>>> from pymacad import ad
>>> ad.bound()
False
>>> ad.accessible('TEST.COM')
False
>>> ad.accessible('FTI.IO')
True
```

### Functions

#### ad.bound()
checks if computer is bound to AD
- returns True or False 
- raises subprocess.CalledProcessError

#### ad.principal(user)
gets principal from AD. If no user is specified, uses the current user. 
- Returns principal
- Raises NotBound, NotReachable or subprocess.CalledProcessError

#### ad.accessible()
checks if domain can be joined. 
- Returns True or False
- raises subprocess.CalledProcessError
    
### Exceptions
- pymacad.ad.NotReachable
- pymacad.ad.NotBound
- subprocess.CalledProcessError

