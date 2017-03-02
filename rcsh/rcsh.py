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

DEFAULT_CONF_FILE = '/etc/rcsh'
DEFAULT_FILTER_DIR = '/etc/rcsh.d'

log_stdin = False
log_stdout = False
log_stderr = False
max_duration = 30 # seconds # not implemented

syslog.openlog('rcsh', syslog.LOG_PID, syslog.LOG_AUTH)

# log to syslog
# get config from conf.d dir
# allow overrides to get config from a diff dir by looking at something like /etc/rcsh


# print('printing some interesting info...')
# print('environment:')
# pprint(os.environ)
# print('argv:')
# print(sys.argv)

# limit possible commands to fixed strings of regexps
# log invocation
# log stdin, stdout, stderr (though perhaps compressed and public key encrypted, or perhap "all" channels)

def get_configuration(configuration_file=DEFAULT_CONF_FILE, filter_dir=DEFAULT_FILTER_DIR):
    """
    """
    pass

def load_whitelists(username, config_dir=DEFAULT_FILTER_DIR):
    """
    """
    exact_allowed = []
    # print(os.path.join(config_dir, '%s.exact*' % username))
    for fn in glob(os.path.join(config_dir, '%s.exact*' % username)):
        # print(fn)
        exact_allowed += [c.strip() for c in open(fn, 'r').readlines()]

    regex_allowed = []
    for fn in glob(os.path.join(config_dir, '%s.regex*' % username)):
        regex_allowed += [c.strip() for c in open(fn, 'r').readlines()]

    return exact_allowed, regex_allowed

def invoke(command_requested, timeout=5):
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



    # check if data was given on stdin
    # # check if data was given on stdin
    # if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    #     syslog.syslog('Invocation for "%s" from %s attempted to pass data over stdin: %s' % (username, source_ip, repr(sys.stdin.readlines())))

    # stdin_lines = []
    # for line in sys.stdin.readlines():
    #     stdin_lines.append(line)

    # check if data was given on stdin
    # only reads one line if it exists
    # ideally we would read all lines up to now, but that seems troublesome ...
    # ... as in readlines block until stdin is closed remotely, not timeout parameter possible
    # ... so we have to use a daemon thread probably to fetch lines from 
    # if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    #     stdin_lines = [sys.stdin.readline()]
    # else:
    #     stdin_lines = []

    # import fcntl
    # fd = sys.stdin.fileno()
    # fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    # fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)



    # stdin_lines = []
    # try:
    #     # for _ in range(100): # read max 100 times
    #     #     stdin_lines.append(sys.stdin.read())
    #     stdin_lines = sys.stdin.read()
    # except IOError as e:
    #     # sort of an EOF signal, seems readline raises a 
    #     # IOError: [Errno 11] Resource temporarily unavailable 
    #     # if there is data to read
    #     # etype, evalue, etb = sys.exc_info()
    #     print(e, dir(e))
    #     # pass if it's indeed this specific exception, otherwise reraise
    #     if e.errno != 11:
    #         raise


    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        stdin_lines = sys.stdin.readline()
    else:
        stdin_lines = []

    # stdin_lines = []
    # start = time.time()
    # while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    #     if (time.time() - start) > 5.0:
    #         break
    #     line = sys.stdin.readline()
    #     print(line,)
    #     if line:
    #         stdin_lines.append(line)
    #     else: # an empty line means stdin has been closed
    #         break
    #     time.sleep(0.1)

    return return_code, stdin_lines

def invoke33(command_requested, timeout=600):
    """
        invoke using python 3.3+ facilities, like waiting with a timeout.
    """
    # execute command, while logging interaction
    p = subprocess.Popen(command_requested, shell=True, stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.stdin.close() # since we do not allow invoked processes to listen to stdin, we close stdin to the subprocess
    try:
        return_code = p.wait(timeout)
    except TimeoutExpired:
        # log timeout
        return -1, []

    # check if data was given on stdin
    # # check if data was given on stdin
    # if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    #     syslog.syslog('Invocation for "%s" from %s attempted to pass data over stdin: %s' % (username, source_ip, repr(sys.stdin.readlines())))

    stdin_lines = []
    for line in sys.stdin.readlines():
        if not line:
            break
        stdin_lines.append(line)

    return return_code, stdin_lines

try:
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

        exact_allowed, regex_allowed, = load_whitelists(username)

        allowed = False
        if command_requested in exact_allowed:
            allowed = True
        else:
            # check against every regexp
            for regexp in regex_allowed:
                if re.match(regexp, command_requested):
                    allowed = True
                    break
        if not allowed:
            # print('This is not allowed, invoke something like:')
            # pprint(exact_allowed)
            # pprint(regex_allowed)
            syslog.syslog('Invocation not allowed for "%s" from %s: %s' % (username, source_ip, command_requested))
            sys.exit(1)

        # print('This would have been allowed.')
        syslog.syslog('Invocation allowed for "%s" from %s: %s' % (username, source_ip, command_requested))

        return_code, stdin_lines = invoke(command_requested)

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

