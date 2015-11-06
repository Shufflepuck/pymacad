import subprocess
import plistlib
from SystemConfiguration import SCDynamicStoreCreate, \
                                SCDynamicStoreCopyValue, \
                                SCDynamicStoreCopyConsoleUser

def _cmd_dsconfigad_show():
    return subprocess.check_output(['dsconfigad', '-show'])

def _get_consoleuser():
    return SCDynamicStoreCopyConsoleUser(None, None, None)[0]

def _dscl(plist=True, nodename='.', scope=None, query=None, user=_get_consoleuser()):
    if not scope:
        scope = '/Users/{0}'.format(user)
    cmd = ['/usr/bin/dscl', nodename, '-read', scope]
    if plist:
        cmd.insert(1, '-plist')
    if query:
        cmd.append(query)
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        if plist:
            return plistlib.readPlistFromString(output)
        else:
            return output
    except subprocess.CalledProcessError:
        return None

def bound():
    try:
        output = _cmd_dsconfigad_show()

        if "Active Directory" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        raise

def searchnodes():
    net_config = SCDynamicStoreCreate(None, 'directory-nodes', None, None)
    nodes = SCDynamicStoreCopyValue(net_config, 'com.apple.opendirectoryd.node:/Search')
    return list(nodes)


def adnode():
    nodes = searchnodes()
    ad_node = [node for node in nodes if 'Active Directory' in node]
    return ad_node[0] if ad_node else None


def domain_dns():
    net_config = SCDynamicStoreCreate(None, 'active-directory', None, None)
    ad_info = SCDynamicStoreCopyValue(net_config, 'com.apple.opendirectoryd.ActiveDirectory')
    return ad_info.get('DomainNameDns')

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

def principal(user=_get_consoleuser()):
    """Returns the principal of the current user when computer is bound"""

    if not bound():
        raise NotBound

    user_path = '/Users/' + user

    try:
        output = _dscl('/Search', query='AuthenticationAuthority', scope=user_path)
        if not output:
            return 'User not found!'
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

def accessible(domain=domain_dns()):
    try:
        dig = _cmd_dig_check(domain)
    except subprocess.CalledProcessError:
        raise
    else:
        if 'ANSWER SECTION' not in dig:
            return False
        else:
            return True

def membership(user=_get_consoleuser()):
    ad_group_info = _dscl(nodename=adnode(), query='memberOf', user=user)
    if ad_group_info:
        groups = [line[line.find('CN=')+3:line.find(',')]
                  for line in ad_group_info.split('\n ') if 'CN=' in line]
        return groups
    else:
        return list()

def realms():
    store = SCDynamicStoreCreate(None, 'default-realms', None, None)
    realms = SCDynamicStoreCopyValue(store, 'Kerberos-Default-Realms')
    return list(realms)


def smb_home(node='.', user=_get_consoleuser()):
    output = _dscl(nodename=node, query='SMBHome', user=user)
    if output and 'No such key:' not in output:
        out_split = output.split(' ')[1]
        smb_home = out_split.replace('\\\\', '/').replace('\\', '/').strip('\n')
        smb_url = '{0}{1}'.format('smb:/', smb_home)
        return smb_url
    else:
        return ''
