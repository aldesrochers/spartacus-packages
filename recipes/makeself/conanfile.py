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


class MakeselfConan(ConanFile):
    name = "makeself"
    version = "2.4.3"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "GPL"
    description = "A self-extracting archiving tool for Unix systems, in 100% shell script."
    homepage = "https://makeself.io/"

    settings = "os", "arch", "compiler"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _autotools = None
    _source_subfolder = "sources"


    def build_requirements(self):
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASE_PATH"):
            self.build_requires("msys2/20200517")

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("makeself-release-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("*", src=os.path.join(self._source_subfolder, "release"), dst="bin")
        os.rename(os.path.join(self.package_folder, "bin", "makeself-{}.run".format(self.version)),
                  os.path.join(self.package_folder, "bin", "makeself.run"))

    def package_info(self):
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))