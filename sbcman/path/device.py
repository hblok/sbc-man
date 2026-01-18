# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Find and explores mounts and paths on the device.
"""

import pathlib

class DevicePaths:

    def get_mounted_filesystems(self):
        """
        Get list of mounted filesystems, excluding special system devices.
        Returns mount points as pathlib.Path objects.
        """
        # Filesystem types to exclude
        excluded_fs_types = {
            'sysfs', 'proc', 'devtmpfs', 'devpts', 'tmpfs', 'securityfs',
            'cgroup', 'cgroup2', 'pstore', 'bpf', 'configfs', 'debugfs',
            'tracefs', 'fusectl', 'fuse.gvfsd-fuse', 'fuse.portal',
            'mqueue', 'hugetlbfs', 'autofs', 'efivarfs', 'binfmt_misc',
            'squashfs', 'overlay', 'nsfs', 'ramfs'
        }

        # Device prefixes to exclude
        excluded_prefixes = ('/sys', '/proc', '/dev', '/run')

        mount_points = []

        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 3:
                        continue

                    device = parts[0]
                    mount_point = parts[1]
                    fs_type = parts[2]

                    # Skip excluded filesystem types
                    if fs_type in excluded_fs_types:
                        continue

                    # Skip excluded mount point prefixes
                    if any(mount_point.startswith(prefix) for prefix in excluded_prefixes):
                        continue

                    # Convert to Path object
                    path = pathlib.Path(mount_point)

                    # Only add if it exists and is a directory
                    if path.exists() and path.is_dir():
                        mount_points.append(path)

        except FileNotFoundError:
            # Fallback for non-Linux systems
            pass

        return mount_points


# Usage example
if __name__ == "__main__":
    mounts = DevicePaths().get_mounted_filesystems()
    
    print("Mounted filesystems:")
    for mount in mounts:
        print(f"  {mount}")
