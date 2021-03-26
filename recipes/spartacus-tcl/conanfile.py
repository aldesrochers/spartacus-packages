# =============================================================================
# Copyright (C) 2021-
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Alexis L. Desrochers (alexisdesrochers@gmail.com)
#
# =============================================================================

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class TclConan(ConanFile):
    name = "spartacus-tcl"
    version = "8.6.11"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "Tcl/Tk"
    description = " Tcl programming language."
    homepage = "https://www.tcl.tk/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _autotools = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        if self.settings.os == "Linux":
            return os.path.join(self.source_folder, self._source_subfolder, "unix")
        else:
            return os.path.join(self.source_folder, self._source_subfolder, "win")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def requirements(self):
        self.requires("spartacus-zlib/1.2.11")

    def config_options(self):
        del self.settings.compiler.version
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported from within Windows bash.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("tcl{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        # arguments
        args = []
        args.append("--enable-threads")
        args.append("--enable-64bit" if self.settings.arch == "x86_64" else "--disable-64bit")
        args.append("--enable-symbols" if self.settings.build_type == "Debug" else "--disable-symbols")
        args.append("--enable-shared" if self.options.shared else "--disable-shared")
        # rules
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(configure_dir=self._configure_path,
                                  args=args)
        return self._autotools

    def build(self):
        os.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TCL"
        self.cpp_info.names["cmake_find_package_multi"] = "TCL"
        # append to PATH
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))
        # TCL_ROOT
        self.env_info.TCL_ROOT = self.package_folder
        self.output.info("Set TCL_ROOT as {}".format(self.package_folder))
        # libs
        self.cpp_info.libs = tools.collect_libs(self)