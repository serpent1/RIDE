#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import time

from robotide.context import SETTINGS
from robotide.spec import LibrarySpec
from robotide.robotapi import normpath
from robotide.publish.messages import RideLogException


class LibraryCache(object):

    def __init__(self):
        self.library_keywords = {}
        self._default_libraries = self._get_default_libraries()
        self._default_kws = self._build_default_kws()

    def add_library(self, name, args=None):
        if not self.library_keywords.has_key(self._key(name, args)):
            kws = []
            try:
                kws = LibrarySpec(name, args).keywords
            except Exception, err:
                RideLogException(message='Importing library %s failed with exception %s.' % (name, err), 
                                 exception=err, level='WARN').publish()
            finally:
                self.library_keywords[self._key(name, args)] = kws

    def _key(self, name, args):
        return (name, tuple(args or ''))

    def get_library_keywords(self, name, args=None):
        if not self.library_keywords.has_key(self._key(name, args)):
            self.add_library(name, args)
        return self.library_keywords[self._key(name, args)]

    def get_default_keywords(self):
        return self._default_kws[:]

    def _build_default_kws(self):
        kws = []
        for spec in self._default_libraries.values():
            kws.extend(spec.keywords)
        return kws

    def _get_default_libraries(self):
        default_libs = {}
        for libsetting in SETTINGS['auto imports'] + ['BuiltIn']:
            name, args = self._get_name_and_args(libsetting)
            default_libs[name] = LibrarySpec(name, args)
        return default_libs

    def _get_name_and_args(self, libsetting):
        parts = libsetting.split('|')
        if len(parts) == 1:
            return parts[0], None
        return parts[0], parts[1:]


class ExpiringCache(object):

    def __init__(self, timeout=0.5):
        self._cache = {}
        self._timeout = timeout

    def get(self, key):
        if key in self._cache:
            key_time, values = self._cache[key]
            if self._is_valid(key_time):
                return values
        return None

    def _is_valid(self, key_time):
        return (time.time() - key_time) < self._timeout

    def put(self, key, values):
        self._cache[key] = (time.time(), values)


    def _get_from_cache(self, source, name):
        try:
            return self._resource_files[name]
        except KeyError:
            path = normpath(os.path.join(os.path.dirname(source), name))
            return self._resource_files[path]

