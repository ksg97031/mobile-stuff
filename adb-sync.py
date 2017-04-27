#!/usr/bin/env python3

import subprocess
import sys
import os
from multiprocessing import Pool

try:
  from pathlib import Path
except ImportError:
  print('python > 3.4 required for running this script')


def adb_shell(*args):
  full_args = ('adb', 'shell') + args
  return subprocess.check_output(full_args).decode()


def sync(pid):
  device_id = adb_shell('settings', 'get', 'secure', 'android_id').strip()
  parent = Path(__file__).resolve().parent
  root = parent / 'rom'
  base = root / device_id
  maps = adb_shell('su', '-c', 'cat /proc/%d/maps' % pid)
  tasks = []
  for line in maps.splitlines():
    try:
      address, perms, offset, dev, inode, pathname = line.split()
    except ValueError:
      continue

    if 'x' in perms and pathname.startswith('/'):
      local_path = base / pathname[1:]
      tasks.append((pathname, local_path))

  print('%d files to sync' % len(tasks))
  pool = Pool(4)
  pool.map(su_pull, tasks)


def su_pull(pair):
  remote, local = pair
  if local.exists():
    return

  print('pulling %s' % remote)
  if not local.parent.exists():
    os.makedirs(local.parent)

  with open(local, 'wb') as out:
    p = subprocess.Popen(['adb', 'shell', 'su', '-c', 'cat %s' % remote], stdout=out)
    p.wait()


if __name__ == '__main__':
  try:
    _, arg = sys.argv
    pid = int(arg)
    sync(pid)

  except (ValueError, IndexError):
    print('Usage: sync.py PID')

