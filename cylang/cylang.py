"""
The main cylang module.

Basic usage (compiles all the compilable modules):

>>> from cylang import cylang
>>> cylang()

"""
import sys
import os
import json
import time
import argparse
from . import compiled
from setuptools import Extension
from cython import cythonize

MODULE_EXT = ['.so', '.dll']

#: A db for the compiled modules
_db_path = os.path.join(compiled.__path__, 'db.json')

COMPILED_MODULES = json.load(open(_db_path))

cylang_parser = argparse.ArgumentParser(description="Cylang command line.")
cylang_parser.add_argument('--compile', action='store_true')
cylang_parser.add_argument('--recompile-all', action='store_true')
cylang_parser.add_argument('--remove-unused', action='store_true')
cylang_parser.add_argument('--clean', action='store_true')


def remove_unused():
    for module, module_info in COMPILED_MODULES.items():
        if not os.path.exists(module_info['path']):
            os.remove(module_info['compiled_path'])
            del COMPILED_MODULES[module]

    json.dump(COMPILED_MODULES, open(_db_path, 'wt'))


def clean():
    for file in os.listdir(compiled.__path__):
        if file.endswith(MODULE_EXT):
            os.remove(file)
    global COMPILED_MODULES
    COMPILED_MODULES = {}
    json.dump(COMPILED_MODULES, open(_db_path, 'wt'))


def cylang(**kwargs):
    """
    Compiles the missing needed modules if '--compile' is provided.
    Compiles all the already compiled modules if '--compile' is provided.
    Imports all the needed modules if no cylang option is provided.

    `kwargs` are kewyword arguments passed to `_search_needed_modules` and
    `cythonize`
    """

    to_import = __search_needed_modules(kwargs.pop('whitelist', []),
                                        kwargs.pop('blacklist', []),
                                        kwargs.pop('only_subdir', ''))
    cli_args = cylang_parser.parse_known_args()
    if cli_args.compile:
        to_compile = {}
        for module_name, module_info in to_import.items():
            compiled_module_info = COMPILED_MODULES.get(module_name)
            if compiled_module_info is None or\
                    compiled_module_info['last_edit'] < module_info['last_edit']:
                to_compile[module_name] = module_info

        __compile(to_compile, **kwargs)
    elif cli_args.recompile_all:
        recompile_all(**kwargs)
    elif cli_args.remove_unused:
        remove_unused()
    elif cli_args.clean:
        clean()
    else:
        __import(to_import)


def recompile_all(**kwargs):
    __compile(COMPILED_MODULES, **kwargs)


def __compile(to_compile, **kwargs):
    """
    Compiles the missing needed modules.

    Return the list of cythonized extensions.

    All the `**kwargs` will be passed to `cythonize`
    """
    extensions = []
    for module, module_info in to_compile.items():
        extensions.append(Extension(module, [module_info['path']]))
        # TODO
        output_name = None
        COMPILED_MODULES[module] = {
            'path': module_info['path'],
            'last_edit': time.time(),
            'compiled_path': os.path.join(
                compiled.__path__,
                output_name
            )
        }

    extensions = cythonize(extensions, build_dir=compiled.__path__, **kwargs)
    json.dump(COMPILED_MODULES, open(_db_path, 'wt'))
    return extensions


def __import(to_import):
    """
    Imports all the needed modules replacing those already imported from python
    files
    """
    sys.path.insert(0, compiled.__path__)
    for module in to_import.keys():
        # another option could be to use the 'compiled_path' in
        # COMPILED_MODULES[module]
        if module in sys.modules:
            del sys.modules[module]
        __import__(module)


def __search_needed_modules(whitelist=[], blacklist=[], only_subdir=''):
    """
    TODO (minor): do this before having imported everything!

    Search for the imported modules and returns a dictionary of module_names,
    each associated with the (already imported) module object.

    Excludes builtin modules and modules in `blacklist`.

    If `whitelist` is not empty, only modules in `whitelist` and not in
    `blacklist` are added.

    If `only_subdir` is set, only modules in the same dir and subdirs
    of the specified path are considered for the addition.

    `whitelist`, `blacklist` and `only_subdir` are used in a `or` fashion.

    """

    out = {}
    for module_name, module in sys.modules:
        needed = False
        if hasattr(module, '__file__') and module.__file__:
            if not module.__file__.endswith(MODULE_EXT):
                # this is a compilable module
                needed = True
                if module in blacklist:
                    needed = False
                if whitelist and module not in whitelist:
                    needed = False
                if only_subdir and not __is_subdir(module.__file__,
                                                   only_subdir):
                    needed = False
                if needed:
                    out[module_name] = {
                        'path': module.__file__,
                        'last_edit': os.path.getmtime(module.__file__)
                    }

    return out


def __is_subdir(p1, p2):
    """
    Returns true if p1 is p2 or its subdirectory.
    If files are used instead of directories, this uses the directory of
    the files.
    """
    if os.path.isfile(p1):
        p1 = os.path.dirname(p1)
    if os.path.isfile(p2):
        p2 = os.path.dirname(p2)
    p1, p2 = os.path.realpath(p1), os.path.realpath(p2)
    return p1 == p2 or p1.startswith(p2 + os.sep)
