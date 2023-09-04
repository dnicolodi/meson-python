# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import importlib.machinery
import os
import pathlib
import sys
import sysconfig

from collections import defaultdict

import packaging.tags
import pytest

import mesonpy
import mesonpy._tags

from .conftest import adjust_packaging_platform_tag


# Test against the wheel tag generated by packaging module.
tag = next(packaging.tags.sys_tags())
ABI = tag.abi
INTERPRETER = tag.interpreter
PLATFORM = adjust_packaging_platform_tag(tag.platform)


def get_abi3_suffix():
    for suffix in importlib.machinery.EXTENSION_SUFFIXES:
        if '.abi3' in suffix:  # Unix
            return suffix
        elif suffix == '.pyd':  # Windows
            return suffix


SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')
ABI3SUFFIX = get_abi3_suffix()


def test_wheel_tag():
    assert str(mesonpy._tags.Tag()) == f'{INTERPRETER}-{ABI}-{PLATFORM}'
    assert str(mesonpy._tags.Tag(abi='abi3')) == f'{INTERPRETER}-abi3-{PLATFORM}'


@pytest.mark.skipif(sys.platform != 'darwin', reason='macOS specific test')
def test_macos_platform_tag(monkeypatch):
    for minor in range(9, 16):
        monkeypatch.setenv('MACOSX_DEPLOYMENT_TARGET', f'10.{minor}')
        assert next(packaging.tags.mac_platforms((10, minor))) == mesonpy._tags.get_platform_tag()
    for major in range(11, 20):
        for minor in range(3):
            monkeypatch.setenv('MACOSX_DEPLOYMENT_TARGET', f'{major}.{minor}')
            assert next(packaging.tags.mac_platforms((major, minor))) == mesonpy._tags.get_platform_tag()


@pytest.mark.skipif(sys.platform != 'darwin', reason='macOS specific test')
def test_python_host_platform(monkeypatch):
    monkeypatch.setenv('_PYTHON_HOST_PLATFORM', 'macosx-12.0-arm64')
    assert mesonpy._tags.get_platform_tag().endswith('arm64')
    monkeypatch.setenv('_PYTHON_HOST_PLATFORM', 'macosx-11.1-x86_64')
    assert mesonpy._tags.get_platform_tag().endswith('x86_64')


def wheel_builder_test_factory(monkeypatch, content, pure=True, limited_api=False):
    files = defaultdict(list)
    files.update({key: [(pathlib.Path(x), os.path.join('build', x)) for x in value] for key, value in content.items()})
    return mesonpy._WheelBuilder(None, None, pathlib.Path(), pathlib.Path(), files, limited_api)


def test_tag_empty_wheel(monkeypatch):
    builder = wheel_builder_test_factory(monkeypatch, {})
    assert str(builder.tag) == 'py3-none-any'


def test_tag_purelib_wheel(monkeypatch):
    builder = wheel_builder_test_factory(monkeypatch, {
        'purelib': ['pure.py'],
    })
    assert str(builder.tag) == 'py3-none-any'


def test_tag_platlib_wheel(monkeypatch):
    builder = wheel_builder_test_factory(monkeypatch, {
        'platlib': [f'extension{SUFFIX}'],
    })
    assert str(builder.tag) == f'{INTERPRETER}-{ABI}-{PLATFORM}'


def test_tag_stable_abi(monkeypatch):
    builder = wheel_builder_test_factory(monkeypatch, {
        'platlib': [f'extension{ABI3SUFFIX}'],
    }, limited_api=True)
    assert str(builder.tag) == f'{INTERPRETER}-abi3-{PLATFORM}'


@pytest.mark.skipif(sys.version_info < (3, 8) and sys.platform == 'win32',
                    reason='Extension modules filename suffix without ABI tags')
def test_tag_mixed_abi(monkeypatch):
    builder = wheel_builder_test_factory(monkeypatch, {
        'platlib': [f'extension{ABI3SUFFIX}', f'another{SUFFIX}'],
    }, pure=False, limited_api=True)
    with pytest.raises(mesonpy.BuildError, match='The package declares compatibility with Python limited API but '):
        assert str(builder.tag) == f'{INTERPRETER}-abi3-{PLATFORM}'
