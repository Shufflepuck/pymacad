import subprocess
import getpass

def _cmd_dsconfigad_show():
    return subprocess.check_output(['dsconfigad', '-show'])

def bound():
    try:
        output = _cmd_dsconfigad_show()

        if "Active Directory" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        raise


def _cmd_dscl_search(user_path):
    return subprocess.check_output(['dscl',
                                     '/Search',
                                     'read',
                                     user_path,
                                     'AuthenticationAuthority'],
                                     stderr=subprocess.STDOUT)

class ProcessError(subprocess.CalledProcessError):
    pass

class NotReachable(Exception):
    pass

class NotBound(Exception):
    pass

def _extract_principal(string):
    import re
    try:
        match = re.search(r'[a-zA-Z0-9+_\-\.]+@[^;]+\.[A-Z]{2,}', string, re.IGNORECASE)
        match = match.group()
    except AttributeError:
        raise
    else:
        return match

def principal(user=getpass.getuser()):
    """Returns the principal of the current user when computer is bound"""

    if not bound():
        raise NotBound


    user_path = '/Users/' + user

    try:
        output = _cmd_dscl_search(user_path)
        result = _extract_principal(output)
    except AttributeError:
        raise NotReachable
    except subprocess.CalledProcessError:
        raise
    else:
        return result

def _cmd_dig_check(domain):
    try:
        dig = subprocess.check_output(['dig', '-t', 'srv', '_ldap._tcp.' + domain])
    except subprocess.CalledProcessError:
        raise
    else:
        return dig

def accessible(domain):
    dig = _cmd_dig_check(domain)
    if 'ANSWER SECTION' not in dig:
        return False
    else:
        return True

