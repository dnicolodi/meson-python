import os
import subprocess

import pytest

import mesonpy


@pytest.mark.parametrize(
    ('args', 'expected'),
    [
        ([], True),
        (['-Dbuildtype=release'], True),
        (['-Dbuildtype=debug'], False),
    ],
    ids=['default', '-Dbuildtype=release', '-Dbuildtype=debug'],
)
def test_ndebug(package_scipy_like, tmp_path, args, expected):
    with mesonpy._project({'setup-args': args}) as project:
        command = subprocess.run(
            ['ninja', '-C', os.fspath(project._build_dir), '-t', 'commands', '../../mypkg/extmod.c^'],
            stdout=subprocess.PIPE, check=True).stdout
        print(command)
        assert (b'-DNDEBUG' in command) == expected
