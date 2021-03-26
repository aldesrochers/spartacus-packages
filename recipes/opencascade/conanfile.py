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

class OpenCascadeConan(ConanFile):
    name = "opencascade"
    version = "7.5.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "LGPL"
    description = ("It's a software development kit (SDK) intended for the development of applications dealing with "
                   "3D CAD data. OCCT includes a set of C++ class libraries providing services for 3D surface and "
                   "solid modeling, visualization, data exchange and rapid application development.")
    homepage = "https://www.opencascade.com/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ApplicationFramework": [True, False],
               "with_DataExchange": [True, False],
               "with_Draw": [True, False],
               "with_FoundationClasses": [True, False],
               "with_Inspector": [True, False],
               "with_ModelingAlgorithms": [True, False],
               "with_ModelingData": [True, False],
               "with_Visualization": [True, False]}
    default_options = {"fPIC": True,
                       "shared": True,
                       "with_ApplicationFramework": True,
                       "with_DataExchange": True,
                       "with_Draw": True,
                       "with_FoundationClasses": True,
                       "with_Inspector": True,
                       "with_ModelingAlgorithms": True,
                       "with_ModelingData": True,
                       "with_Visualization": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # internals
    _cmake = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def build_requirements(self):
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASE_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("buildhelpers/1.0.0@{}/{}".format(self.user, self.channel))

    def requirements(self):
        self.requires("freetype/2.10.4")
        self.requires("tcl/8.6.11@{}/{}".format(self.user, self.channel))
        self.requires("tk/8.6.11@{}/{}".format(self.user, self.channel))
        self.requires("qt5/5.15.2@{}/{}".format(self.user, self.channel))

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

        # always used shared prerequisites
        self.options["freetype"].shared = True
        self.options["tcl"].shared = True
        self.options["tk"].shared = True
        self.options["qt5"].shared = True

    def source(self):
        import buildhelpers
        buildhelpers.googledrive_get(**self.conan_data["sources"][self.version])
        os.rename("opencascade-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["3RDPARTY_FREETYPE_DIR"] = self.deps_cpp_info["freetype"].rootpath
        self._cmake.definitions["3RDPARTY_TCL_DIR"] = self.deps_cpp_info["tcl"].rootpath
        self._cmake.definitions["3RDPARTY_TK_DIR"] = self.deps_cpp_info["tk"].rootpath
        self._cmake.definitions["3RDPARTY_QT_DIR"] = self.deps_cpp_info["qt5"].rootpath
        self._cmake.definitions["BUILD_LIBRARY_TYPE"] = "Shared" if self.options.shared else "Static"
        self._cmake.definitions["BUILD_Inspector"] = self.options.with_Inspector
        self._cmake.definitions["BUILD_MODULE_ApplicationFramwork"] = self.options.with_ApplicationFramework
        self._cmake.definitions["BUILD_MODULE_DataExchange"] = self.options.with_DataExchange
        self._cmake.definitions["BUILD_MODULE_Draw"] = self.options.with_Draw
        self._cmake.definitions["BUILD_MODULE_FoundationClasses"] = self.options.with_FoundationClasses
        self._cmake.definitions["BUILD_MODULE_ModelingAlgorithms"] = self.options.with_ModelingAlgorithms
        self._cmake.definitions["BUILD_MODULE_ModelingData"] = self.options.with_ModelingData
        self._cmake.definitions["BUILD_MODULE_Visualization"] = self.options.with_Visualization
        self._cmake.definitions["BUILD_RESOURCES"] = False
        self._cmake.definitions["BUILD_SAMPLES_QT"] = False
        self._cmake.definitions["INSTALL_DIR_LAYOUT"] = "Unix"
        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()


