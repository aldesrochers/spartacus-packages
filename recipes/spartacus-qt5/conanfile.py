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


class SpartacusQt5(ConanFile):
    name = "spartacus-qt5"
    version = "5.15.2"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "LGPL"
    description = "The Qt framework."
    homepage = "https://www.qt.io/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "target": "ANY",
               "skip_qt3d": [True, False],
               "skip_qtactiveqt": [True, False],
               "skip_qtandroidextras": [True, False],
               "skip_qtbase": [True, False],
               "skip_qtcharts": [True, False],
               "skip_qtconnectivity": [True, False],
               "skip_qtdatavis3d": [True, False],
               "skip_qtdeclarative": [True, False],
               "skip_qtdoc": [True, False],
               "skip_qtgamepad": [True, False],
               "skip_qtgraphicaleffects": [True, False],
               "skip_qtimageformats": [True, False],
               "skip_qtlocation": [True, False],
               "skip_qtlottie": [True, False],
               "skip_qtmacextras": [True, False],
               "skip_qtmultimedia": [True, False],
               "skip_qtnetworkauth": [True, False],
               "skip_qtpurchasing": [True, False],
               "skip_qtquick3d": [True, False],
               "skip_qtquickcontrols": [True, False],
               "skip_qtquickcontrols2": [True, False],
               "skip_qtquicktimeline": [True, False],
               "skip_qtremoteobjects": [True, False],
               "skip_qtscript": [True, False],
               "skip_qtscxml": [True, False],
               "skip_qtsensors": [True, False],
               "skip_qtserialbus": [True, False],
               "skip_qtserialport": [True, False],
               "skip_qtspeech": [True, False],
               "skip_qtsvg": [True, False],
               "skip_qttools": [True, False],
               "skip_qttranslations": [True, False],
               "skip_qtvirtualkeyboard": [True, False],
               "skip_qtwayland": [True, False],
               "skip_qtwebchannel": [True, False],
               "skip_qtwebengine": [True, False],
               "skip_qtwebglplugin": [True, False],
               "skip_qtwebsockets": [True, False],
               "skip_qtwebview": [True, False],
               "skip_qtwinextras": [True, False],
               "skip_qtx11extras": [True, False],
               "skip_qtxmlpatterns": [True, False],
               "with_system_doubleconversion": [True, False],
               "with_system_fontconfig": [True, False],
               "with_system_freetype": [True, False],
               "with_system_glib": [True, False],
               "with_system_harfbuzz": [True, False],
               "with_system_icu": [True, False],
               "with_system_jpeg": [True, False],
               "with_system_openssl": [True, False],
               "with_system_pcre": [True, False],
               "with_system_png": [True, False],
               "with_system_sqlite": [True, False],
               "with_system_zlib": [True, False]}
    default_options = {"fPIC": True,
                       "shared": True,
                       "target": None,
                       "skip_qt3d": True,
                       "skip_qtactiveqt": True,
                       "skip_qtandroidextras": True,
                       "skip_qtbase": False,
                       "skip_qtcharts": True,
                       "skip_qtconnectivity": True,
                       "skip_qtdatavis3d": True,
                       "skip_qtdeclarative": False,
                       "skip_qtdoc": True,
                       "skip_qtgamepad": True,
                       "skip_qtgraphicaleffects": True,
                       "skip_qtimageformats": True,
                       "skip_qtlocation": True,
                       "skip_qtlottie": True,
                       "skip_qtmacextras": True,
                       "skip_qtmultimedia": True,
                       "skip_qtnetworkauth": True,
                       "skip_qtpurchasing": True,
                       "skip_qtquick3d": True,
                       "skip_qtquickcontrols": True,
                       "skip_qtquickcontrols2": True,
                       "skip_qtquicktimeline": True,
                       "skip_qtremoteobjects": True,
                       "skip_qtscript": False,
                       "skip_qtscxml": True,
                       "skip_qtsensors": True,
                       "skip_qtserialbus": True,
                       "skip_qtserialport": True,
                       "skip_qtspeech": True,
                       "skip_qtsvg": True,
                       "skip_qttools": False,
                       "skip_qttranslations": True,
                       "skip_qtvirtualkeyboard": True,
                       "skip_qtwayland": True,
                       "skip_qtwebchannel": True,
                       "skip_qtwebengine": True,
                       "skip_qtwebglplugin": True,
                       "skip_qtwebsockets": True,
                       "skip_qtwebview": True,
                       "skip_qtwinextras": True,
                       "skip_qtx11extras": True,
                       "skip_qtxmlpatterns": True,
                       "with_system_doubleconversion": True,
                       "with_system_fontconfig": True,
                       "with_system_freetype": True,
                       "with_system_glib": True,
                       "with_system_harfbuzz": True,
                       "with_system_icu": True,
                       "with_system_jpeg": True,
                       "with_system_openssl": True,
                       "with_system_pcre": True,
                       "with_system_png": True,
                       "with_system_sqlite": True,
                       "with_system_zlib": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    exports_sources = ["patches/**"]
    short_paths = True

    # internals
    _autotools = None
    _source_subfolder = "sources"
    _build_subfolder = "build"


    @property
    def _configure_path(self):
        return os.path.join(self.build_folder, self._source_subfolder)

    @property
    def _xplatform(self):
        if self.settings.os == "Linux":
            if self.settings.compiler == "gcc":
                if self.settings.arch == "x86":
                    return "linux-g++-32"
                else:
                    return "linux-g++"
        elif self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                return "win32-g++"
            else:
                return "win32-msvc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # cross-building ?
        if not tools.cross_building(self):
            del self.options.target
        # platform specifics
        if self.settings.os == "Windows":
            del self.options.with_system_fontconfig
            del self.options.with_system_glib
        # configure extras
        if self.settings.os == "Windows":
            del self.options.qtandroidextras
            del self.options.qtmacextras
            del self.options.qtx11extras
        elif self.settings.os == "Linux":
            del self.options.qtandroidextras
            del self.options.qtmacextras
            del self.options.qtwinextras

    def build_requirements(self):
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASE_PATH"):
            self.build_requires("msys2/20200517")
        if tools.os_info.is_windows:
            self.build_requires("strawberryperl/5.30.0.1")
            self.build_requires("winflexbison/2.5.24")
        elif tools.os_info.is_linux:
            self.build_requires("bison/3.7.1")
            self.build_requires("flex/2.6.4")

    def requirements(self):
        self.requires("double-conversion/3.1.5") if self.options.with_system_doubleconversion else None
        if self.settings.os == "Linux":
            self.requires("fontconfig/2.13.93") if self.options.with_system_fontconfig else None
        self.requires("freetype/2.10.4") if self.options.with_system_freetype else None
        if self.settings.os == "Linux":
            self.requires("glib/2.68.0") if self.options.with_system_glib else None
        self.requires("harfbuzz/2.8.0") if self.options.with_system_harfbuzz else None
        self.requires("icu/68.2") if self.options.with_system_icu else None
        self.requires("libjpeg/9d") if self.options.with_system_jpeg else None
        self.requires("openssl/1.1.1j") if self.options.with_system_openssl else None
        self.requires("pcre2/10.36") if self.options.with_system_pcre else None
        self.requires("libpng/1.6.37") if self.options.with_system_png else None
        self.requires("sqlite3/3.35.1") if self.options.with_system_sqlite else None
        self.requires("zlib/1.2.11") if self.options.with_system_zlib else None

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

        # cross-building ?
        if tools.cross_building(self):
            if not self.options.target:
                raise ConanInvalidConfiguration("A value for option 'target' must be provided.")

        # always used shared prerequisites
        if self.options.with_system_doubleconversion:
            self.options["double-conversion"].shared = True
        if self.settings.os == "Linux":
            if self.options.with_system_fontconfig:
                self.options["fontconfig"].shared = True
        if self.options.with_system_freetype:
            self.options["freetype"].shared = True
        if self.settings.os =="Linux":
            if self.options.with_system_glib:
                self.options["glib"].shared = True
        if self.options.with_system_harfbuzz:
            self.options["harfbuzz"].shared = True
        if self.options.with_system_icu:
            self.options["icu"].shared = True
        if self.options.with_system_jpeg:
            self.options["libjpeg"].shared = True
        if self.options.with_system_openssl:
            self.options["openssl"].shared = True
        if self.options.with_system_pcre:
            self.options["pcre2"].shared = True
        if self.options.with_system_png:
            self.options["libpng"].shared = True
        if self.options.with_system_sqlite:
            self.options["sqlite3"].shared = True
        if self.options.with_system_zlib:
            self.options["zlib"].shared = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("qt-everywhere-src-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        # arguments
        args = []
        if tools.os_info.is_linux:
            args.append("{}/configure".format(self._configure_path))
        else:
            args.append("{}/configure.bat".format(self._configure_path))
        args.append("")
        args.append("-opengl desktop")
        args.append("-opensource")
        args.append("-confirm-license")
        args.append("-nomake examples")
        args.append("-nomake tests")
        args.append("-prefix {}".format(self.package_folder))
        args.append("-debug" if self.settings.build_type == "Debug" else "-release")
        args.append("-shared" if self.options.shared else "-static")
        # cross-building ?
        if tools.cross_building(self):
            args.append("-xplatfom {}".format(self._xplatform))
            args.append("-device-option CROSS_COMPILE={}".format(self.options.target))
        # components
        args.append("-skip qt3d") if self.options.skip_qt3d else None
        args.append("-skip qtactiveqt") if self.options.skip_qtactiveqt else None
        #args.append("-skip qtandroidextras") if self.options.skip_qtandroidextras else None
        args.append("-skip qtandroidextras")
        args.append("-skip qtbase") if self.options.skip_qtbase else None
        args.append("-skip qtcharts") if self.options.skip_qtcharts else None
        args.append("-skip qtconnectivity") if self.options.skip_qtconnectivity else None
        args.append("-skip qtdatavis3d") if self.options.skip_qtdatavis3d else None
        args.append("-skip qtdeclarative") if self.options.skip_qtdeclarative else None
        args.append("-skip qtdoc") if self.options.skip_qtdoc else None
        args.append("-skip qtgamepad") if self.options.skip_qtgamepad else None
        args.append("-skip qtgraphicaleffects") if self.options.skip_qtgraphicaleffects else None
        args.append("-skip qtimageformats") if self.options.skip_qtimageformats else None
        args.append("-skip qtlocation") if self.options.skip_qtlocation else None
        args.append("-skip qtlottie") if self.options.skip_qtlottie else None
        #args.append("-skip qtmacextras") if self.options.skip_qtmacextras else None
        args.append("-skip qtmacextras")
        args.append("-skip qtmultimedia") if self.options.skip_qtmultimedia else None
        args.append("-skip qtnetworkauth") if self.options.skip_qtnetworkauth else None
        args.append("-skip qtpurchasing") if self.options.skip_qtpurchasing else None
        args.append("-skip qtquick3d") if self.options.skip_qtquick3d else None
        args.append("-skip qtquickcontrols") if self.options.skip_qtquickcontrols else None
        args.append("-skip qtquickcontrols2") if self.options.skip_qtquickcontrols2 else None
        args.append("-skip qtquicktimeline") if self.options.skip_qtquicktimeline else None
        args.append("-skip qtremoteobjects") if self.options.skip_qtremoteobjects else None
        args.append("-skip qtscript") if self.options.skip_qtscript else None
        args.append("-skip qtscxml") if self.options.skip_qtscxml else None
        args.append("-skip qtsensors") if self.options.skip_qtsensors else None
        args.append("-skip qtserialbus") if self.options.skip_qtserialbus else None
        args.append("-skip qtserialport") if self.options.skip_qtserialport else None
        args.append("-skip qtspeech") if self.options.skip_qtspeech else None
        args.append("-skip qtsvg") if self.options.skip_qtsvg else None
        args.append("-skip qttools") if self.options.skip_qttools else None
        args.append("-skip qttranslations") if self.options.skip_qttranslations else None
        args.append("-skip qtvirtualkeyboard") if self.options.skip_qtvirtualkeyboard else None
        args.append("-skip qtwayland") if self.options.skip_qtwayland else None
        args.append("-skip qtwebchannel") if self.options.skip_qtwebchannel else None
        args.append("-skip qtwebengine") if self.options.skip_qtwebengine else None
        args.append("-skip qtwebglplugin") if self.options.skip_qtwebglplugin else None
        args.append("-skip qtwebsockets") if self.options.skip_qtwebsockets else None
        args.append("-skip qtwebview") if self.options.skip_qtwebview else None
        if self.settings.os == "Windows":
            args.append("-skip qtwinextras") if self.options.skip_qtwinextras else None
        else:
            args.append("-skip qtwinextras")
        if self.settings.os == "Linux":
            args.append("-skip qtx11extras") if self.options.skip_qtx11extras else None
        else:
            args.append("-skip qtx11extras")
        args.append("-skip qtxmlpatterns") if self.options.skip_qtxmlpatterns else None
        # 3rdParty configuration
        if self.settings.os == "Linux":
            args.append("-fontconfig") if self.options.with_system_fontconfig else None
            args.append("-glib") if self.options.with_system_glib else None
        args.append("-icu") if self.options.with_system_icu else None
        args.append("-sqlite") if self.options.with_system_sqlite else None
        args.append("-system-doubleconversion" if self.options.with_system_doubleconversion else "-qt-doubleconversion")
        args.append("-system-freetype" if self.options.with_system_freetype else "-qt-freetype")
        args.append("-system-harfbuzz" if self.options.with_system_freetype else "-qt-harfbuzz")
        args.append("-system-libjpeg" if self.options.with_system_jpeg else "-qt-libjpeg")
        args.append("-system-libpng" if self.options.with_system_png else "-qt-png")
        args.append("-system-pcre" if self.options.with_system_zlib else "-qt-pcre")
        args.append("-system-zlib" if self.options.with_system_zlib else "-qt-zlib")
        if self.options.with_system_openssl:
            args.append("--openssl-linked")
            args.append("OPENSSL_PREFIX={}".format(self.deps_cpp_info["openssl"].rootpath))
        # add prerequisites include/lib/definitions in configure command
        for package in self.deps_cpp_info.deps:
            args += ["-I \"%s\"" % s for s in self.deps_cpp_info[package].include_paths]
            args += ["-D %s" % s for s in self.deps_cpp_info[package].defines]
            args += ["-L \"%s\"" % s for s in self.deps_cpp_info[package].lib_paths]
        # rules
        cmd = ""
        for arg in args:
            cmd += "{} ".format(arg)
        self.run(cmd, win_bash=tools.os_info.is_windows)
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return self._autotools

    def build(self):
        # apply patches
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        # build
        os.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Qt5"
        self.cpp_info.names["cmake_find_package_multi"] = "Qt5"
        # append to PATH
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))