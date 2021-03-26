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


class SpartacusSystem(ConanFile):
    name = "spartacus-system"
    version = "1.0.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "GPL"
    description = "A system configuration for the Spartacus project."
    homepage = url

    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = {}
    default_user = "aldesrochers"
    default_channel = "testing"

    # internals
    _mingw_gcc_version = "8.1.0"


    def config_options(self):
        del self.settings.compiler.version
        del self.settings.compiler.libcxx
        del self.settings.compiler.threads

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.linux_distro in ["archlinux", "manjaro"]:
                package_name = "gcc"
                installer = tools.SystemPackageTool(tool=tools.PacManTool())
            else:
                package_name = "gcc"
                installer = tools.SystemPackageTool()
                self.output.warn("Unknown Linux detected. Try to locate gcc.")
            installer.install(package_name, update=True)

    def configure(self):
        if tools.os_info.is_linux and not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux while building on Linux.")
        if tools.os_info.is_windows and not self.settings.os in ["Windows"]:
            raise ConanInvalidConfiguration("Only supported on Windows while building on Windows.")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Only supported with gcc compilers.")
        if tools.get_env("CONAN_BASH_PATH"):
            raise ConanInvalidConfiguration("Not supported from within Windows bash.")

    def build(self):
        if self.settings.os == "Windows" and self.settings.arch == "x86":
            tools.get(**self.conan_data["binaries"]["windows"][self._mingw_gcc_version]["x86"])
        elif self.settings.os == "Windows" and self.settings.arch == "x86_64":
            tools.get(**self.conan_data["binaries"]["windows"][self._mingw_gcc_version]["x86_64"])



