#!/usr/bin/env python3
"""
Restrict shell invocations using a whitelist

Inspired by lshell and bdsh:
- https://github.com/ghantoos/lshell
- https://raymii.org/s/software/bdsh.html
- https://github.com/RaymiiOrg/boa-diminish-restricted-shell/

"""

import os, sys, getpass, re, shlex, syslog, traceback, subprocess, select, time
from pprint import pprint
from glob import glob
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DEFAULT_CONF_FILE = '/etc/rcsh'
DEFAULT_FILTER_DIR = '/etc/rcsh.d'
DEFAULT_TIMEOUT = 30 # seconds # not implemented
DEFAULT_LOG_STDIN = True  # not implemented
DEFAULT_LOG_STDOUT = True  # not implemented
DEFAULT_LOG_STDERR = True  # not implemented

def setup_logging():
    syslog.openlog('rcsh', syslog.LOG_PID, syslog.LOG_AUTH)

def get_configuration(configuration_file=DEFAULT_CONF_FILE):
    """
    """
    config = configparser.ConfigParser({
        'ConfigDir': DEFAULT_FILTER_DIR,
        'Timeout': DEFAULT_TIMEOUT,
    })
    config.read(configuration_file)
    return config

def load_whitelists(username, filter_dir=DEFAULT_FILTER_DIR):
    """
    """
    exact_allowed = []
    # print(os.path.join(filter_dir, '%s.exact*' % username))
    for fn in glob(os.path.join(filter_dir, '%s.exact*' % username)):
        print(fn)
        with open(fn, 'r') as f:
            exact_allowed += [c.strip() for c in f.readlines() if not c.strip().startswith('#')]

    regex_allowed = []
    for fn in glob(os.path.join(filter_dir, '%s.regex*' % username)):
        with open(fn, 'r') as f:
            for c in f.readlines():
                c = c.strip()
                if c.startswith('#'):
                    # it's a comment, so skip it
                    continue
                if not (c.startswith('^') and c.endswith('$')):
                    # open ended regular expressions are too risky, there for not allowed
                    syslog.syslog('Skipping "%s" as a valid regex since it does not start with "^" and end with "$"' % c)
                    continue
                regex_allowed.append(c)

    return exact_allowed, regex_allowed

def is_invocation_allowed(command_requested, exact_allowed=[], regex_allowed=[]):
    """
        Check if command_requested is an element of exact_allowed or if it
        matches a pattern in regex_allowed. If so, then return True.
    """
    allowed = False
    if command_requested in exact_allowed:
        allowed = True
    else:
        for regexp in regex_allowed:
            if re.match(regexp, command_requested):
                allowed = True
                break
    return allowed

def invoke(command_requested, timeout=DEFAULT_TIMEOUT):
    """
    """
    p = subprocess.Popen(command_requested, shell=True, stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.stdin.close() # since we do not allow invoked processes to listen to stdin, we close stdin to the subprocess
    try:
        return_code = p.wait(timeout)
    except TypeError:
        # most likely this is a python version lower than 3.3
        start = time.time()
        while p.poll() is None and (time.time() - start) < timeout:
            time.sleep(0.1) # nicer than a pass, which would cause a lot of CPU usage
        return_code = -1
        syslog.syslog('Invocation timed out')
    except subprocess.TimeoutExpired: # works on python < 3.3 because a known exception is caught first
        return_code = -1
        syslog.syslog('Invocation timed out')

    # We are also interested in data sent to stdin. This isn't allowed, and may 
    # be interesting for forensics
    # Beware, this code is a bit iffy. In fact, reading from stdin seems iffy
    # to me.
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        stdin_lines = sys.stdin.readline()
    else:
        stdin_lines = []

    return return_code, stdin_lines

def main():
    try:
        setup_logging()
        config = get_configuration()

        username = getpass.getuser()
        if 'SSH_CLIENT' in os.environ:
            source_ip = os.environ['SSH_CLIENT'].split()[0]
        else:
            source_ip = 'unknown source ip'

        if len(sys.argv) <= 1:
            # not called with an argument
            print('Interactive login not permitted.')
            # log something about the invocation
            syslog.syslog('Interactive login not permitted for "%s" from %s' % (username, source_ip))
            sys.exit(1)
        elif len(sys.argv) == 3 and sys.argv[1] == '-c': 
            # normal remote invocation
            command_requested = sys.argv[2]
            # print('You attempted to invoke "%s"' % command_requested)

            timeout = config.getint('DEFAULT', 'timout')
            filter_dir = config.get('DEFAULT', 'filter_dir')

            exact_allowed, regex_allowed, = load_whitelists(username, filter_dir)

            allowed = is_invocation_allowed(command_requested, exact_allowed, regex_allowed)

            if not allowed:
                syslog.syslog('Invocation not allowed for "%s" from %s: %s' % (username, source_ip, command_requested))
                sys.exit(1)

            # print('This would have been allowed.')
            syslog.syslog('Invocation allowed for "%s" from %s: %s' % (username, source_ip, command_requested))

            return_code, stdin_lines = invoke(command_requested, timeout)

            if stdin_lines:
                syslog.syslog('Invocation for "%s" from %s attempted to pass data over stdin: %s' % (username, source_ip, repr(stdin_lines)))

            syslog.syslog('Invocation allowed for "%s" from %s finished with exit code %d' % (username, source_ip, return_code))
            sys.exit(return_code)
            # capture exit code and exit with that same code
        else:
            # print('Unexpected invocation.')
            # log something about the invocation
            syslog.syslog('Unexpected invocation by "%s" from %s, argv:\n%s' % (username, source_ip, repr(sys.argv)))
            sys.exit(1)
    except:
        # log information about invocation and exception
        # but don't leak information
        etype, evalue, etb = sys.exc_info()
        if etype == SystemExit:
            # normal, just raise
            raise
        # print('Unexpected error occured during invocation.')
        syslog.syslog('Unexpected error occured during invocation by "%s" from %s:\n%s' % (username, source_ip, traceback.format_exc()))
        # print(etype, evalue, etb)
        sys.exit(1)

if __name__ == "__main__":
    main()

