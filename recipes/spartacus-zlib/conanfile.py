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
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class SpartacusZlib(ConanFile):
    name = "spartacus-zlib"
    version = "1.2.11"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library"
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    homepage = "https://zlib.net/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _cmake = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def config_options(self):
        del self.settings.compiler.version
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            del self.options.fPIC


    def build_requirements(self):
        self.build_requires("spartacus-toolchain/1.0.0@{}/{}".format(self.user, self.channel))
        self.build_requires("cmake/3.19.5")

    def configure(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux.")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Only supported with gcc compilers.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported within Windows bash.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zlib-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder,
                              build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))
        # collect libraries
        self.cpp_info.libs = tools.collect_libs(self)

    def deploy(self):
        if self.settings.os == "Windows" and self.settings.arch == "x86":
            root = "i686-spartacus-mingw32"
        elif self.settings.os == "Windows" and self.settings.arch == "x86_64":
            root = "x86_64-spartacus-mingw32"
        elif self.settings.os == "Linux" and self.settings.arch == "x86":
            root = "i686-spartacus-linux"
        elif self.settings.os == "Linux" and self.settings.arch == "x86_64":
            root = "x86_64-spartacus-linux"
        self.copy("*", src=self.package_folder, dst=root)