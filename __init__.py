import subprocess
import getpass

def cmd_dsconfigad_show():
    return subprocess.check_output(['dsconfigad', '-show']) 

def bound_to_ad():
    try:
        output = cmd_dsconfigad_show()

        if "Active Directory" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError as error:
        raise


def cmd_dscl_search(user_path):
    return subprocess.check_output(['dscl',
                                     '/Search',
                                     'read',
                                     user_path,
                                     'AuthenticationAuthority'],
                                     stderr=subprocess.STDOUT)

class NotReachable(Exception):
    pass

class NotBound(Exception):
    pass

def get_principal_from_ad(user=getpass.getuser()):
    """Returns the principal of the current user when computer is bound"""

    if not bound_to_ad():
        raise NotBound

    import re

    user_path = '/Users/' + user

    print user_path
    try:
        output = cmd_dscl_search(user_path)
        match = re.search(r'[a-zA-Z0-9+_\-\.]+@[^;]+\.[A-Z]{2,}', output, re.IGNORECASE)
        match = match.group()

    except (subprocess.CalledProcessError, AttributeError) as error:
        raise NotReachable

    else:
        return match

def domain_isacessible(domain):
    dig = subprocess.check_output(['dig', '-t', 'srv', '_ldap._tcp.' + domain])
    if 'ANSWER SECTION' not in dig:
        raise NotReachable
    else:
        return True
