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

import os, shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class SpartacusToolchain(ConanFile):
    name = "spartacus-toolchain"
    version = "1.0.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "GPL"
    description = "A toolchain for the Spartacus project."
    homepage = url

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "target": ["i686-spartacus-mingw32", "i686-spartacus-linux",
                          "x86_64-spartacus-mingw32", "x86_64-spartacus-linux",
                          None]}
    default_options = {"fPIC": True,
                       "target": None}
    default_user = "aldesrochers"
    default_channel = "testing"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        del self.settings.compiler.version

    def requirements(self):
        if self.options.target in ["i686-spartacus-mingw32", "x86_64-spartacus-mingw32"]:
            self.requires("spartacus-mingw-gcc/1.0.0@{}/{}".format(self.user, self.channel))
        elif self.options.target in ["i686-spartacus-linux", "x86_64-spartacus-linux"]:
            self.requires("spartacus-linux-gcc/1.0.0@{}/{}".format(self.user, self.channel))

    def configure(self):
        if tools.os_info.is_linux and not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux while building on Linux.")
        if tools.os_info.is_windows and not self.settings.os in ["Windows"]:
            raise ConanInvalidConfiguration("Only supported on Windows while building on Windows.")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Only supported with gcc compilers.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported from within Windows bash.")

        # check for valid self.options.target
        settings_target = getattr(self, "settings_target", None)
        if settings_target is None:
            if self.settings.os == "Windows":
                if self.settings.arch == "x86":
                    self.options.target = "i686-spartacus-mingw32"
                else:
                    self.options.target = "x86_64-spartacus-mingw32"
            else:
                if self.settings.arch == "x86":
                    self.options.target = "i686-spartacus-linux"
                else:
                    self.options.target = "x86_64-spartacus-linux"
        else:
            if self.options.target:
                raise ConanInvalidConfiguration("A value for option 'target' should not be provided.")
            if settings_target.os not in ["Windows", "Linux"]:
                raise ConanInvalidConfiguration("Only supported for Windows and Linux targets.")
            if settings_target.os == "Windows":
                if settings_target.arch == "x86":
                    self.options.target = "i686-spartacus-mingw32"
                else:
                    self.options.target = "x86_64-spartacus-mingw32"
            else:
                if settings_target.arch == "x86":
                    self.options.target = "i686-spartacus-linux"
                else:
                    self.options.target = "x86_64-spartacus-linux"

        # passing configuration
        if self.options.target in ["i686-spartacus-mingw32", "x86_64-spartacus-mingw32"]:
            print("{}".format(self.options.target))
            self.options["spartacus-mingw-gcc"].target = self.options.target
        elif self.options.target in ["i686-spartacus-linux", "x86_64-spartacus-linux"]:
            self.options["spartacus-linux-gcc"].target = self.options.target

    def package_info(self):
        self.env_info.CHOST = "{}".format(self.options.target)
        if tools.os_info.is_windows:
            self.env_info.AR = "{}-ar.exe".format(self.options.target)
            self.env_info.AS = "{}-as.exe".format(self.options.target)
            self.env_info.CC = "{}-gcc.exe".format(self.options.target)
            self.env_info.CXX = "{}-g++.exe".format(self.options.target)
            self.env_info.RANLIB = "{}-ranlib.exe".format(self.options.target)
            self.env_info.RC = "{}-windres.exe".format(self.options.target)
            self.env_info.STROP = "{}-strip.exe".format(self.options.target)
        else:
            self.env_info.AR = "{}-ar".format(self.options.target)
            self.env_info.AS = "{}-as".format(self.options.target)
            self.env_info.CC = "{}-gcc".format(self.options.target)
            self.env_info.CXX = "{}-g++".format(self.options.target)
            self.env_info.RANLIB = "{}-ranlib".format(self.options.target)
            self.env_info.RC = "{}-windres".format(self.options.target)
            self.env_info.STRIP = "{}-strip".format(self.options.target)

        self.output.info("Set AR as {}".format(self.env_info.AR))
        self.output.info("Set AS as {}".format(self.env_info.AS))
        self.output.info("Set CC as {}".format(self.env_info.CC))
        self.output.info("Set CXX as {}".format(self.env_info.CXX))
        self.output.info("Set RANLIB as {}".format(self.env_info.RANLIB))
        self.output.info("Set RC as {}".format(self.env_info.RC))
        self.output.info("Set STRIP as {}".format(self.env_info.STRIP))






