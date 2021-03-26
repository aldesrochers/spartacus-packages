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


class SpartacusLinuxGcc(ConanFile):
    name = "spartacus-linux-gcc"
    version = "1.0.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = "LGPL (glibc) GPLv3 (linux, gcc, binutils)"
    description = "A complete linux toolchain based on mingw-w64, gcc, glibc and binutils."
    homepage = "https://www.kernel.org/"

    settings = "os", "arch", "compiler"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "target": ["i686-spartacus-linux", "x86_64-spartacus-linux", None],
               "with_fortran": [True, False]}
    default_options = {"fPIC": True,
                       "shared": True,
                       "target": None,
                       "with_fortran": True}
    default_user = "aldesrochers"
    default_channel = "testing"

    no_copy_source = True

    # internals
    _binutils_version = "2.36"
    _linux_version = "5.11.1"
    _gcc_version = "10.2.0"
    _glibc_version = "2.33"
    _binutils_source_subfolder = "sources-binutils"
    _linux_source_subfolder = "sources-linux"
    _gcc_source_subfolder = "sources-gcc"
    _glibc_source_subfolder = "sources-glibc"
    _binutils_build_subfolder = "build-binutils"
    _gcc_build_subfolder = "build-gcc"
    _glibc_build_subfolder = "build-glibc"
    _sysroot_build_subfolder = "build-sysroot"


    @property
    def _binutils_configure_path(self):
        return os.path.join(self.source_folder, self._binutils_source_subfolder)

    @property
    def _gcc_configure_path(self):
        return os.path.join(self.source_folder, self._gcc_source_subfolder)

    @property
    def _glibc_configure_path(self):
        return os.path.join(self.source_folder, self._glibc_source_subfolder)

    @property
    def _linux_configure_path(self):
        return os.path.join(self.source_folder, self._linux_source_subfolder)

    @property
    def _sysroot_build_path(self):
        return os.path.join(self.build_folder, self._sysroot_build_subfolder)

    @property
    def _is_64bit_target(self):
        return self.options.target == "x86_64-spartacus-linux"

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.linux_distro in ["archlinux", "manjaro"]:
                package_name = "gcc"
                installer = tools.SystemPackageTool(tool=tools.PacManTool())
            else:
                package_name = "gcc"
                installer = tools.SystemPackageTool()
                self.output.warn("Unknown Linux detected. Try to locate gcc.")
            installer.install(package_name)
        elif tools.os_info.is_linux and self.settings.os == "Windows":
            if tools.os_info.linux_distro in ["archlinux", "manjaro"]:
                package_name = "mingw-w64-gcc"
                installer = tools.SystemPackageTool(tool=tools.PacManTool())
            else:
                package_name = "mingw-w64-gcc"
                installer = tools.SystemPackageTool()
                self.output.warn("Unknown Linux detected. Try to locate mingw-w64-gcc.")
            installer.install(package_name)
            if self.settings.arch == "x86":
                os.environ["CC"] = os.path.join("usr", "bin", "i686-w64-mingw32-gcc")
                os.environ["CXX"] = os.path.join("usr", "bin", "i686-w64-mingw32-g++")
            else:
                os.environ["CC"] = os.path.join("usr", "bin", "x86_64-w64-mingw32-gcc")
                os.environ["CXX"] = os.path.join("usr", "bin", "x86_64-w64-mingw32-g++")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("autoconf/2.69")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        del self.settings.compiler.version

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
            if not self.options.target:
                raise ConanInvalidConfiguration("A value for option 'target' must be provided.")
        else:
            if settings_target.os not in ["Linux"]:
                raise ConanInvalidConfiguration("Only supported for Linux targets.")
            if settings_target.arch == "x86":
                self.options.target = "i686-spartacus-linux"
            else:
                self.options.target = "x86_64-spartacus-linux"

    def source(self):
        tools.get(**self.conan_data["sources"]["binutils"][self._binutils_version])
        tools.get(**self.conan_data["sources"]["linux"][self._linux_version])
        tools.get(**self.conan_data["sources"]["gcc"][self._gcc_version])
        tools.get(**self.conan_data["sources"]["glibc"][self._glibc_version])
        os.rename("binutils-{}".format(self._binutils_version), self._binutils_source_subfolder)
        os.rename("gcc-{}".format(self._gcc_version), self._gcc_source_subfolder)
        os.rename("linux-{}".format(self._linux_version), self._linux_source_subfolder)
        os.rename("glibc-{}".format(self._glibc_version), self._glibc_source_subfolder)

        # download additional gcc prerequisites
        with tools.chdir(self._gcc_source_subfolder):
            self.run("contrib/download_prerequisites", win_bash=tools.os_info.is_windows)

    def _build_binutils(self):
        args = []
        args.append("--disable-multilib")
        args.append("--target={}".format(self.options.target))
        args.append("--enable-lto")
        args.append("--enable-nls")
        args.append("--enable-install-libiberty")
        args.append("--enable-plugins")
        args.append("--enable-64-bit-bfd") if self._is_64bit_target else None
        args.append("--prefix={}".format(self._sysroot_build_path))
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=self._binutils_configure_path,
                            args=args)
        autotools.make()
        autotools.install()

    def _build_linux_headers(self):
        target = "{}".format(self.options.target)
        arch = "x86" if target == "i686-spartacus-linux" else "x86_64"
        with tools.chdir(self._linux_configure_path):
            self.run("make ARCH={} INSTALL_HDR_PATH={}/{} headers_install".format(arch, self._sysroot_build_path, target),
                     win_bash=tools.os_info.is_windows)

    def _build_gcc_core(self):
        languages = "c, c++"
        languages += ", fortran" if self.options.with_fortran else ""
        args = []
        # TODO!! Bug with lib sanitizer.
        args.append("--disable-libsanitizer")
        args.append("--disable-multilib")
        args.append("--target={}".format(self.options.target))
        args.append("--disable-nls")
        #args.append("--enable-bootstrap")
        args.append("--enable-libatomic")
        #args.append("--enable-libgomp")
        args.append("--enable-lto")
        #args.append("--enable-graphite")
        args.append("--enable-shared") if self.options.shared else args.append("--disable-shared")
        args.append("--enable-static")
        #args.append("--enable-threads=posix")
        args.append("--prefix={}".format(self._sysroot_build_path))
        args.append("--enable-languages={}".format(languages))
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build_vars = autotools.vars
        if self.settings.arch == "x86":
            build_vars['LDFLAGS'] = ' -Wl,--large-address-aware,--disable-dynamicbase'
        else:
            build_vars['LDFLAGS'] = ' -Wl,--disable-dynamicbase'
        autotools.configure(configure_dir=self._gcc_configure_path,
                            args=args)
        autotools.make(target="all-gcc")
        autotools.make(target="install-gcc")

    def _build_glibc_startup(self):
        target = "{}".format(self.options.target)
        args = []
        args.append("--host={}".format(target))
        args.append("--target={}".format(target))
        args.append("--prefix={}/{}".format(self._sysroot_build_path, target))
        args.append("--with-headers={}/{}/include".format(self._sysroot_build_path, target))
        args.append("--disable-multilib")
        args.append("--disable-werror")
        args.append("libc_cv_forced_unwind=yes")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        vars_build = autotools.vars
        vars_build["CFLAGS"] = "-O3"
        autotools.configure(configure_dir=self._glibc_configure_path,
                            vars=vars_build,
                            args=args)
        with tools.environment_append(vars_build):
            self.run("make install-bootstrap-headers=yes install-headers", win_bash=tools.os_info.is_windows)
            self.run("make -j4 csu/subdir_lib", win_bash=tools.os_info.is_windows)
            self.run("install csu/crt1.o csu/crti.o csu/crtn.o {}/{}/lib".format(self._sysroot_build_path, target),
                     win_bash=tools.os_info.is_windows)
            self.run("{}-gcc -nostdlib -nostartfiles -shared -x c /dev/null -o {}/{}/lib/libc.so".format(target, self._sysroot_build_path, target),
                     win_bash=tools.os_info.is_windows)
            self.run("touch {}/{}/include/gnu/stubs.h".format(self._sysroot_build_path, target),
                     win_bash=tools.os_info.is_windows)

    def _build_gcc_support(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.make(target="all-target-libgcc")
        autotools.make(target="install-target-libgcc")

    def _build_glibc(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.make()
        autotools.install()

    def _build_gcc(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.make()
        autotools.install()

    def build(self):
        # append sysroot to PATH
        sysroot_bin_path = os.path.join(self._sysroot_build_path, "bin")
        os.environ["PATH"] = "{}{}{}".format(sysroot_bin_path, os.pathsep, os.getenv("PATH"))
        #self.run("unset LIBRARY_PATH CPATH C_INCLUDE_PATH PKG_CONFIG_PATH CPLUS_INCLUDE_PATH LD_LIBRARY_PATH",
        #         win_bash=tools.os_info.is_windows)

        # build binutils
        os.mkdir(self._binutils_build_subfolder)
        with tools.chdir(self._binutils_build_subfolder):
            self._build_binutils()
        # build linux-headers
        self._build_linux_headers()
        # build gcc-core
        os.mkdir(self._gcc_build_subfolder)
        with tools.chdir(self._gcc_build_subfolder):
            self._build_gcc_core()
        # build glibc-startup
        os.mkdir(self._glibc_build_subfolder)
        with tools.chdir(self._glibc_build_subfolder):
            self._build_glibc_startup()
        # build gcc-supprt
        with tools.chdir(self._gcc_build_subfolder):
            self._build_gcc_support()
        # build glibc
        with tools.chdir(self._glibc_build_subfolder):
            self._build_glibc()
        # build gcc
        with tools.chdir(self._gcc_build_subfolder):
            self._build_gcc()

    def package(self):
        self.copy("*", src=self._sysroot_build_path, dst="", keep_path=True)

    def package_info(self):
        binary_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binary_path)
        self.output.info("Added to PATH : {}".format(binary_path))

    def deploy(self):
        self.copy("*", src="", dst="")


if __name__ == '__main__':
    os.system("conan create . ")

