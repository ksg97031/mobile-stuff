#!/usr/bin/env python3

import subprocess
import sys
import os
import re

from multiprocessing import Pool

try:
    from pathlib import Path
except ImportError:
    print('python > 3.4 required for running this script')


def adb_shell(*args):
    full_args = ('adb', 'shell') + args
    return subprocess.check_output(full_args).decode()


def adb_pull(remote, local):
    try:
        return subprocess.check_output(['adb', 'pull', remote, local])
    except subprocess.CalledProcessError:
        print('failed to pull %s' % remote)


def su(command):
    return adb_shell('su', '-c', command)


def su_copy(path):
    migrate = Path('/sdcard/migrate')
    dest = migrate / path[1:]
    print('pulling %s' % path)
    try:
        su('[ -f {1} ] && mkdir -p {0}; [ ! -f {2} ] && cp -r {1} {2}'.format(dest.parent, path, dest))
    except subprocess.CalledProcessError:
        print('failed to copy: %s' % path)


class Sync(object):
    def __init__(self, arg):
        try:
            pid = int(arg)
        except ValueError:
            # package name?
            pid = adb_shell('set `ps | grep %s` && echo $2' % arg)
            if not pid:
                raise RuntimeError('Unknown package name or keyword {0}.' % arg)
            pid = int(pid)

        self.pid = pid


    def get_deviceid(self):
        device_id = adb_shell('settings', 'get', 'secure', 'android_id').strip()
        print('device id: %s' % device_id)
        parent = Path(__file__).resolve().parent
        root = parent / 'rom'
        self.base = root / device_id


    def exec(self):
        self.get_deviceid()

        probe = '/sdcard/migrate/system/bin/sh'
        tasks = [] if adb_shell('ls', probe).strip() == probe else \
            ['/system/bin/', '/system/lib/', '/vendor/lib/', '/system/framework']
        maps = su('cat /proc/%d/maps' % self.pid)
        for line in maps.splitlines():
            try:
                address, perms, offset, dev, inode, pathname = line.split()
            except ValueError:
                continue

            if 'x' in perms and pathname.startswith('/') and \
                not pathname.startswith('/system') and \
                not 're.frida.server' in pathname:
                tasks.append(pathname)

        
        pool = Pool(4)
        pool.map(su_copy, tasks)
        adb_pull('/sdcard/migrate', self.base)
        print('files pull to %s' % self.base)
        print('set solib-search-path %s' % self.base)


if __name__ == '__main__':
    try:
        _, arg = sys.argv
    except IndexError:
        print('Usage: sync.py PID or PACKAGE')
        sys.exit(0)

    Sync(arg).exec()
