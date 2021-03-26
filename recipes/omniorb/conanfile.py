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


class OmniorbConan(ConanFile):
    name = "omniorb"
    version = "4.3.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "LGPL"
    description = "omniORB is a robust high performance CORBA ORB for C++ and Python."
    homepage = "http://omniorb.sourceforge.net/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _autotools = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        return os.path.join(self.build_folder, self._source_subfolder)

    def build_requirements(self):
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASE_PATH"):
            self.build_requires("msys2/20200517")

    def requirements(self):
        self.requires("openssl/1.1.1j")
        self.requires("python/3.8.8@{}/{}".format(self.user, self.channel))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported from within Windows bash.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        # always link to static python
        self.options["python"].shared = False

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("omniORB-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        # arguments
        args = []
        args.append("--with-openssl={}".format(self.deps_cpp_info["openssl"].rootpath))
        args.append("--disable-static" if self.options.shared else "--enable-static")
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


