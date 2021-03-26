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


class QtCreatorConan(ConanFile):
    name = "qt-creator"
    version = "4.14.1"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "LGPL"
    description = "The Qt creator IDE."
    homepage = "https://www.qt.io/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _autotools = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        return os.path.join(self.build_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASE_PATH"):
            self.build_requires("msys2/20200517")

    def requirements(self):
        self.requires("qt5/5.15.2@{}/{}".format(self.user, self.channel))

    def configure(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux.")
        if self.settings.os == "Windows" and not self.settings.compiler in ["gcc", "Visual Studio"]:
            raise ConanInvalidConfiguration("Only supported on Windows with gcc or MSVC.")
        if self.settings.os == "Linux" and not self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("Only supported on Linux with gcc.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported from within Windows bash.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        # always link to qt5-shared
        self.options["qt5"].shared = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("qt-creator-opensource-src-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        if tools.os_info.is_linux:
            qmake = os.path.join(self.deps_cpp_info["qt5"].rootpath, "bin", "qmake")
        else:
            qmake = os.path.join(self.deps_cpp_info["qt5"].rootpath, "bin", "qmake.exe")
        cmd = "{} {}".format(qmake, self._configure_path)
        self.run(cmd, win_bash=tools.os_info.is_windows)
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return self._autotools

    def build(self):
        os.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.install(args=["INSTALL_ROOT={}".format(self.package_folder)])

    def package_info(self):
        # append to PATH
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))