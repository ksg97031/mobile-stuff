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


def copy_system(base, remote_migrate):
  remote_system_copy = '%s/system/' % remote_migrate
  su('[ ! -d {0} ] && mkdir -p {0} && cp -r /system/bin /system/lib {0}'.format(remote_system_copy))


def sync(pid):
  device_id = adb_shell('settings', 'get', 'secure', 'android_id').strip()
  parent = Path(__file__).resolve().parent
  root = parent / 'rom'
  base = root / device_id
  migrate = Path('/sdcard/migrate')
  copy_system(base, migrate)

  maps = su('cat /proc/%d/maps' % pid)
  tasks = []
  for line in maps.splitlines():
    try:
      address, perms, offset, dev, inode, pathname = line.split()
    except ValueError:
      continue

    if 'x' in perms and pathname.startswith('/'):
      component = pathname[1:]
      local_path = base / component
      remote_migrate = migrate / component
      tasks.append((pathname, remote_migrate, local_path))

  pool = Pool(4)
  pool.map(su_pull, tasks)


def su_pull(args):
  remote, migrate, local = args

  print('pulling %s' % remote)
  if not local.parent.exists():
    os.makedirs(local.parent)

  su('[ ! -f {1} ] cp -u {0} {1}'.format(remote, migrate))
  adb_pull(migrate, local)


if __name__ == '__main__':
  try:
    _, arg = sys.argv
    pid = int(arg)
    sync(pid)

  except (ValueError, IndexError):
    print('Usage: sync.py PID')

