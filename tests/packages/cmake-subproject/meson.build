# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('cmake-subproject', ['c', 'cpp', 'cython'], version: '1')

dep = dependency('cmaketest')

py = import('python').find_installation()

py.extension_module(
    'cmakesubproject',
    'cmakesubproject.pyx',
    dependencies: dep,
    override_options: ['cython_language=cpp'],
    install: true,
)
