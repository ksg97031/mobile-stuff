#!/usr/bin/env python3

import subprocess
import sys
import os
import base64
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


def pull_sys(base):
  for path in ['system/bin/', 'system/lib/', 'vendor/lib/']:
    remote = Path('/') / path
    local = base / path
    if not local.exists():
      print(adb_pull(remote, local))


def sync(pid):
  device_id = adb_shell('settings', 'get', 'secure', 'android_id').strip()
  parent = Path(__file__).resolve().parent
  root = parent / 'rom'
  base = root / device_id
  migrate = Path('/sdcard/migrate')
  pull_sys(base)

  maps = su('cat /proc/%d/maps' % pid)
  tasks = []
  for line in maps.splitlines():
    try:
      address, perms, offset, dev, inode, pathname = line.split()
    except ValueError:
      continue

    if 'x' in perms and pathname.startswith('/') and not pathname.startswith('/system'):
      component = pathname[1:]
      local_path = base / component
      remote_migrate = migrate / component
      tasks.append((pathname, remote_migrate, local_path))

  pool = Pool(4)
  pool.map(su_pull, tasks)
  print('set solib-search-path %s' % base)


def su_pull(args):
  remote, migrate, local = args

  print('pulling %s' % remote)
  if not local.parent.exists():
    os.makedirs(local.parent)

  try:
    su('mkdir -p {0}; [ ! -f {2} ] && cp {1} {2}'.format(migrate.parent, remote, migrate))
    adb_pull(migrate, local)
  except:
    pass


if __name__ == '__main__':
  try:
    _, arg = sys.argv
    pid = int(arg)
    sync(pid)

  except (ValueError, IndexError):
    print('Usage: sync.py PID')

