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


class PythonConan(ConanFile):
    name = "python"
    version = "3.8.8"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/packages"
    topics = ("spartacus", "conan", name)

    license = "PSF"
    description = "A high-level scripting language"
    homepage = "https://www.python.org/"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_optimizations": [True, False]}
    default_options = {"fPIC": True,
                       "shared": True,
                       "with_optimizations": False}
    default_user = "aldesrochers"
    default_channel = "testing"

    exports_sources = ["patches/**"]

    # internals
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.build_folder, "Python-{}".format(self.version))

    @property
    def _build_subfolder(self):
        path = os.path.join(self.build_folder, "build-python")
        os.makedirs(path) if not os.path.exists(path) else None
        return path

    @property
    def _configure_subfolder(self):
        if self.settings.compiler == "gcc":
            return self._source_subfolder
        else:
            return os.path.join(self._source_subfolder, "PCBuild")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        # check if cross-building, need python on build host
        settings_build = getattr(self, "settings_build", None)
        if settings_build != None:
            if self.settings_build.os != self.settings.os:
                self.build_requires("python/{}@{}/{}".format(self.version, self.user, self.channel))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only supported on Windows and Linux.")
        if not self.settings.compiler in ["gcc", "Visual Studio"]:
            raise ConanInvalidConfiguration("Only supported with gcc and MSVC compilers.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def requirements(self):
        if self.settings.compiler == "gcc":
            self.requires("zlib/1.2.11")
            self.requires("xz_utils/5.2.5")
            self.requires("bzip2/1.0.8")
            self.requires("expat/2.2.10")
            #self.requires("mpdecimal/2.5.0@{}/{}".format(self.user, self.channel))
            self.requires("libffi/3.3")
            #self.requires("openssl/1.1.1j")
            self.requires("sqlite3/3.34.1")
            self.requires("tcl/8.6.11@{}/{}".format(self.user, self.channel))
            self.requires("tk/8.6.11@{}/{}".format(self.user, self.channel))

    def _env_mingw(self):
        # setup some env variables
        os.environ["ac_cv_working_tzset"] = "no"
        os.environ["ac_cv_header_dlfcn_h"] = "no"
        os.environ["ac_cv_lib_dl_dlopen"] = "no"
        os.environ["ac_cv_have_decl_RTLD_GLOBAL"] = "no"
        os.environ["ac_cv_have_decl_RTLD_LAZY"] = "no"
        os.environ["ac_cv_have_decl_RTLD_LOCAL"] = "no"
        os.environ["ac_cv_have_decl_RTLD_NOW"] = "no"
        os.environ["ac_cv_have_decl_RTLD_DEEPBIND"] = "no"
        os.environ["ac_cv_have_decl_RTLD_MEMBER"] = "no"
        os.environ["ac_cv_have_decl_RTLD_NODELETE"] = "no"
        os.environ["ac_cv_have_decl_RTLD_NOLOAD"] = "no"

    def _patch_mingw(self):
        with tools.chdir("Python-{}".format(self.version)):
            for i in os.listdir("../patches/mingw"):
                if os.path.splitext(i)[1] == ".patch":
                    try:
                        self.run("patch -Nbp1 -f -i ../patches/mingw/{}".format(i),
                                 win_bash=tools.os_info.is_windows)
                    except:
                        print("Failed to apply patch {}".format(i))
            self.run("autoreconf -vfi", win_bash=tools.os_info.is_windows)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        args = []
        args.append("--enable-shared") if self.options.shared else args.append("--disable-shared")
        args.append("--enable-optimizations") if self.options.with_optimizations else None
        args.append("--enable-profiling")
        args.append("--with-nt-threads") if self.settings.os == "Windows" else None
        args.append("--with-pydebug") if self.settings.build_type == "Debug" else None
        args.append("--with-system-expat")
        args.append("--with-system-ffi")
        #args.append("--with-system-libmpdec")
        #args.append("--with-openssl={}".format(self.deps_cpp_info["openssl"].rootpath))
        args.append("--without-ensurepip")
        args.append("--without-c-locale-coercion")
        args.append("--enable-loadable-sqlite-extensions")

        self._autotools = AutoToolsBuildEnvironment(self)
        env_build_vars = self._autotools.vars
        if self.settings.os == "Windows":
            env_build_vars['CFLAGS'] += " -fwrapv -D__USE_MINGW_ANSI_STDIO=1 -D_WIN32_WINNT=0x0601  -O0 -ggdb"
            env_build_vars['CXXFLAGS'] += " -fwrapv -D__USE_MINGW_ANSI_STDIO=1 -D_WIN32_WINNT=0x0601 -O0 -ggdb"
        self._autotools.configure(vars=env_build_vars,
                                  configure_dir=self._configure_subfolder,
                                  args=args)
        return self._autotools

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._patch_mingw()
            self._env_mingw()
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._env_mingw()
        with tools.chdir(self._build_subfolder):
            autotools = self._configure_autotools()
            autotools.install()


if __name__ == '__main__':
    os.system("conan create . --profile mingw64")