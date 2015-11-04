# pymacad

## pymacad.ad

I would suggest to use `from pymacad import ad` -- then call using ad.xxx

### Functions

#### ad.bound()
checks if computer is bound to AD
- returns True or False 
- raises CalledProcessError

#### ad.principal(user)
gets principal from AD. If no user is specified, uses the current user. 
- Returns principal
- Raises NotBound, NotReachable or subprocess.CalledProcessError

#### ad.accessible()
checks if domain can be joined. 
- Returns True 
- Raises NotReachable
    
### Exceptions
- pymacad.ad.NotReachable
- pymacad.ad.NotBound
- subprocess.CalledProcessError

