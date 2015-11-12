import subprocess
from pymacad import ad

_incorrect_pass_attempts = 0

def _keychain(action_type, item_type, args, return_code=False):
    import os
    if item_type not in ['generic', 'internet']:
        raise Exception()
    if action_type not in ['add', 'find', 'delete']:
        raise Exception()
    action = '{0}-{1}-password'.format(action_type, item_type)
    user_keychain = os.path.expanduser('~/Library/Keychains/login.keychain')
    cmd = ['/usr/bin/security', action] + args + [user_keychain]
    if return_code:
        return subprocess.call(cmd)
    else:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return out
        except subprocess.CalledProcessError as e:
            return None


def _cmd_klist(flag=None):
    import json
    cmd = ['/usr/bin/klist', '--json']
    if flag:
        cmd.append(flag)
    klist_output = subprocess.check_output(cmd)
    return json.loads(klist_output)


def check_keychain(principal=None):
    if principal:
        username, realm = ad._split_principal(principal)
    else:
        if not ad.bound():
            raise ad.NotBound
        realm = ad.realms()[0]
        username=ad._get_consoleuser()
    security_args = [
        '-a', username,
        '-l', realm.upper() + ' (' + username + ')',
        '-s', realm.upper(),
        '-c', 'aapl'
    ]
    return True if _keychain('find', 'generic', security_args) else False


def pass_to_keychain(principal, password):
    """Saves password to keychain for use by kinit."""
    username, realm = ad._split_principal(principal)
    security_args = [
        '-a', username,
        '-l', realm,
        '-s', realm,
        '-c', 'aapl',
        '-T', '/usr/bin/kinit',
        '-w', str(password)
    ]
    return _keychain('add', 'generic', security_args)


def test_kerberos_password(principal, password):
    """Runs the kinit command with supplied password."""
    renew1 = subprocess.Popen(['echo', password], stdout=subprocess.PIPE)
    renew2 = subprocess.Popen(['kinit','-l','10h','--renewable',
                               '--password-file=STDIN','--keychain',
                               ad._format_principal(principal)],
                               stderr=subprocess.PIPE,
                               stdin=renew1.stdout,
                               stdout=subprocess.PIPE)
    renew1.stdout.close()

    out = renew2.communicate()[1]
    if 'incorrect' in out or 'unknown' in out:
        return False
    elif out == '':
        return True
    elif 'revoked' in out:
        return 'Account Disabled'
    else:
        return out


def kinit_keychain_command(principal):
    """Runs the kinit command with keychain password."""
    if not check_keychain(principal):
        return False
    try:
        subprocess.check_output(['/usr/bin/kinit', '-l', '10h', '--renewable',
                                 '--keychain', ad._format_principal(principal)])
        return True
    except:
        return False


def refresh_ticket():
    try:
        subprocess.check_output(['/usr/bin/kinit', '--renew'],
                                 stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def principal_fromcache():
    '''Returns the principal from cache. This works for bound
       and unbound computers. Bound machines should use principal()'''
    cache = _cmd_klist()
    return cache.get('principal')


def destroy(credential=None, cache=None, principal=None):
    '''Wrapper around kdestroy. Deletes all kerberos tickets if no values are
       provided.'''
    if credential:
        flag = '--credential={0}'.format(ad._format_principal(credential))
    elif cache:
        flag = '--cache={0}'.format(cache)
    elif principal:
        flag = '--principal={0}'.format(ad._format_principal(principal))
    else:
        flag = '--all'
    cmd = ['/usr/bin/kdestroy', flag]
    try:
        out = subprocess.check_output(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def tickets(details=False):
    caches = _cmd_klist('--all-content')
    if caches:
        if details:
            tickets = caches.get('tickets')
        else:
            tickets = list()
            for cache in caches.get('tickets'):
                for ticket in cache.get('tickets'):
                    tickets.append(ticket)
        return tickets
    else:
        return None


def caches(details=False):
    out = _cmd_klist('--list-all')
    if out:
        if details:
            caches = out
        else:
            caches = [cache.get('Cache name') for cache in out]
        return caches
    else:
        return list()
