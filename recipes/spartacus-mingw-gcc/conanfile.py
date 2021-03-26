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


class SpartacusMingwGcc(ConanFile):
    name = "spartacus-mingw-gcc"
    version = "1.0.0"
    author = "Alexis L. Desrochers <alexisdesrochers@gmail.com>"
    url = "https://github.com/aldesrochers/spartacus-packages"
    topics = ("spartacus", "conan", name)

    license = ["BSD", "GPL"]
    description = "A complete toolchain based on mingw-w64 & gcc."
    homepage = ["http://mingw-w64.org/doku.php", "https://gcc.gnu.org/"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_fortran": [True, False],
               "target": ["i686-spartacus-mingw32",
                          "x86_64-spartacus-mingw32",
                          None]}
    default_options = {"fPIC": True,
                       "shared": True,
                       "with_fortran": True,
                       "target": None}
    default_user = "aldesrochers"
    default_channel = "testing"

    exports_sources = ["patches/**"]

    # internals
    _binutils_version = "2.36"
    _gcc_version = "10.2.0"
    _mingw_version = "8.0.0"
    _binutils_source_subfolder = "sources-binutils"
    _binutils_build_subfolder = "build-binutils"
    _gcc_source_subfolder = "sources-gcc"
    _gcc_build_subfolder = "build-gcc-core"
    _mingw_source_subfolder = "sources-mingw"
    _headers_build_subfolder = "build-headers"
    _crt_build_subfolder = "build-crt"
    _winpthreads_build_subfolder = "build-winpthreads"
    _sysroot_build_subfolder = "build-sysroot"

    @property
    def _binutils_configure_path(self):
        return os.path.join(self.build_folder, self._binutils_source_subfolder)

    @property
    def _gcc_configure_path(self):
        return os.path.join(self.build_folder, self._gcc_source_subfolder)

    @property
    def _crt_configure_path(self):
        return os.path.join(self.build_folder, self._mingw_source_subfolder, "mingw-w64-crt")

    @property
    def _headers_configure_path(self):
        return os.path.join(self.build_folder, self._mingw_source_subfolder, "mingw-w64-headers")

    @property
    def _winpthreads_configure_path(self):
        return os.path.join(self.build_folder, self._mingw_source_subfolder, "mingw-w64-libraries", "winpthreads")

    @property
    def _sysroot_build_path(self):
        return os.path.join(self.build_folder, self._sysroot_build_subfolder)

    @property
    def _is_64bit_target(self):
        return self.options.target == "x86_64-spartacus-mingw32"

    @property
    def _host_platform(self):
        if tools.os_info.is_linux and self.settings.os == "Windows":
            if self.settings.arch == "x86":
                return "i686-w64-mingw32"
            else:
                return "x86_64-w64-mingw32"
        return None

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.linux_distro in ["archlinux", "manjaro"]:
                package_name = "gcc"
                installer = tools.SystemPackageTool(tool=tools.PacManTool())
            else:
                package_name = "gcc"
                installer = tools.SystemPackageTool()
                self.output.warn("Unknown Linux detected. Try to locate gcc.")
            installer.install(package_name)
            if self.settings.os == "Windows":
                if tools.os_info.linux_distro in ["archlinux", "manjaro"]:
                    package_name = "mingw-w64-gcc"
                    installer = tools.SystemPackageTool(tool=tools.PacManTool())
                else:
                    package_name = "mingw-w64-gcc"
                    installer = tools.SystemPackageTool()
                    self.output.warn("Unknown Linux detected. Try to locate mingw-w64-gcc.")
                installer.install(package_name)

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("autoconf/2.69")

    def config_options(self):
        del self.settings.compiler.version
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            del self.options.fPIC


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
            if settings_target.os not in ["Windows"]:
                raise ConanInvalidConfiguration("Only supported for Windows targets.")
            if settings_target.arch == "x86":
                self.options.target = "i686-spartacus-mingw32"
            else:
                self.options.target = "x86_64-spartacus-mingw32"

    def source(self):
        tools.get(**self.conan_data["sources"]["binutils"][self._binutils_version])
        tools.get(**self.conan_data["sources"]["mingw"][self._mingw_version])
        tools.get(**self.conan_data["sources"]["gcc"][self._gcc_version])
        os.rename("binutils-{}".format(self._binutils_version), self._binutils_source_subfolder)
        os.rename("gcc-{}".format(self._gcc_version), self._gcc_source_subfolder)
        os.rename("mingw-w64-v{}".format(self._mingw_version), self._mingw_source_subfolder)

        # download additional gcc prerequisites
        with tools.chdir(self._gcc_source_subfolder):
            self.run("contrib/download_prerequisites", win_bash=tools.os_info.is_windows)

    def _build_binutils(self):
        args = []
        args.append("--disable-multilib")
        args.append("--enable-lto")
        args.append("--enable-nls")
        args.append("--enable-install-libiberty")
        args.append("--enable-plugins")
        args.append("--enable-64-bit-bfd") if self._is_64bit_target else None
        args.append("--prefix={}".format(self._sysroot_build_path))
        args.append("--with-sysroot={}".format(self.package_folder))
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=self._binutils_configure_path,
                            host=self._host_platform,
                            target=self.options.target,
                            args=args)
        autotools.make()
        autotools.install()

    def _build_headers(self):
        args = []
        args.append("--prefix={}/{}".format(self._sysroot_build_path, self.options.target))
        args.append("--enable-sdk=all")
        args.append("--with-default-msvcrt=msvcrt")
        args.append("--enable-idl")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=self._headers_configure_path,
                            host=self.options.target,
                            args=args)
        autotools.make()
        autotools.install()

        # additional configuration
        os.makedirs(os.path.join(self._sysroot_build_path, "{}".format(self.options.target), "lib"), exist_ok=True)
        if self.settings.os == "Linux":
            os.symlink(os.path.join(self._sysroot_build_path, "{}".format(self.options.target)),
                       os.path.join(self._sysroot_build_path, "mingw"))
            os.symlink(os.path.join(self._sysroot_build_path, "{}".format(self.options.target), "lib"),
                       os.path.join(self._sysroot_build_path, "{}".format(self.options.target), "lib64"))
        else:
            shutil.copytree(os.path.join(self._sysroot_build_path, "{}".format(self.options.target)),
                            os.path.join(self._sysroot_build_path, "mingw"))
            shutil.copytree(os.path.join(self._sysroot_build_path, "{}".format(self.options.target), "lib"),
                            os.path.join(self._sysroot_build_path, "{}".format(self.options.target), "lib64"))

    def _build_gcc_core(self):
        languages = "c, c++"
        languages += ", fortran" if self.options.with_fortran else ""
        args = []
        args.append("--disable-multilib")
        args.append("--disable-nls")
        #args.append("--enable-bootstrap")
        args.append("--enable-libatomic")
        #args.append("--enable-libgomp")
        args.append("--enable-lto")
        args.append("--enable-graphite")
        args.append("--enable-shared") if self.options.shared else args.append("--disable-shared")
        args.append("--enable-static")
        args.append("--enable-threads=posix")
        args.append("--prefix={}".format(self._sysroot_build_path))
        args.append("--with-sysroot={}".format(self._sysroot_build_path))
        args.append("--enable-languages={}".format(languages))
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build_vars = autotools.vars
        if self.settings.arch == "x86":
            build_vars['LDFLAGS'] = ' -Wl,--large-address-aware,--disable-dynamicbase'
        else:
            build_vars['LDFLAGS'] = ' -Wl,--disable-dynamicbase'
        autotools.configure(configure_dir=self._gcc_configure_path,
                            host=self._host_platform,
                            target=self.options.target,
                            args=args)
        autotools.make(target="all-gcc")
        autotools.make(target="install-gcc")

    def _build_crt(self):
        args = []
        args.append("--prefix={}/{}".format(self._sysroot_build_path, self.options.target))
        args.append("--with-sysroot={}/{}".format(self._sysroot_build_path, self.options.target))
        args.append("--disable-multilib")
        args.append("--enable-sdk=all")
        args.append("--with-default-msvcrt=msvcrt")
        args.append("--enable-wildcard")
        args.append("--enable-lib32") if not self._is_64bit_target else args.append("--disable-lib32")
        args.append("--enable-lib64") if self._is_64bit_target else args.append("--disable-lib64")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=self._crt_configure_path,
                            host=self.options.target,
                            args=args)
        autotools.make()
        autotools.install()

    def _build_winpthreads(self):
        args = []
        args.append("--prefix={}/{}".format(self._sysroot_build_path, self.options.target))
        args.append("--with-sysroot={}/{}".format(self._sysroot_build_path, self.options.target))
        args.append("--enable-shared") if self.options.shared else args.append("--disable-shared")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=self._winpthreads_configure_path,
                            host=self.options.target,
                            args=args)
        autotools.make()
        autotools.install()

    def _build_gcc(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.make()
        autotools.install()

    def build(self):
        sysroot_bin_path = os.path.join(self._sysroot_build_path, "bin")
        os.environ["PATH"] = "{}{}{}".format(sysroot_bin_path, os.pathsep, os.getenv("PATH"))

        # patch mingw
        for patch in self.conan_data["patches"]["mingw"][self._mingw_version]:
            tools.patch(**patch)
        shutil.copyfile(os.path.join("patches", "mingw-{}".format(self._mingw_version), "Makefile.in"),
                        os.path.join(self._mingw_source_subfolder, "mingw-w64-crt", "Makefile.in"))
        shutil.copyfile(os.path.join("patches", "mingw-{}".format(self._mingw_version), "windowsapp_1st.mri"),
                        os.path.join(self._mingw_source_subfolder, "mingw-w64-crt", "lib-common", "windowsapp_1st.mri"))
        shutil.copyfile(os.path.join("patches", "mingw-{}".format(self._mingw_version), "windowsapp_2nd.mri"),
                        os.path.join(self._mingw_source_subfolder, "mingw-w64-crt", "lib-common", "windowsapp_2nd.mri"))

        # patch for spartacus support
        with tools.chdir(self._binutils_source_subfolder):
            tools.replace_in_file("configure.ac", "-w64", "-spartacus")
            self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows, run_environment=True)
        with tools.chdir(self._gcc_source_subfolder):
            # add support for spartacus-mingw
            tools.replace_in_file("configure.ac", "w64-", "spartacus-")
            tools.replace_in_file("gcc/config.gcc", "w64-", "spartacus-")
            tools.replace_in_file("libstdc++-v3/configure.host", "w64-", "spartacus-")
            self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows, run_environment=True)

        # build binutils
        os.mkdir(self._binutils_build_subfolder)
        with tools.chdir(self._binutils_build_subfolder):
            self._build_binutils()
        # build headers
        os.mkdir(self._headers_build_subfolder)
        with tools.chdir(self._headers_build_subfolder):
            self._build_headers()
        # build gcc-core
        os.mkdir(self._gcc_build_subfolder)
        with tools.chdir(self._gcc_build_subfolder):
            self._build_gcc_core()
        # build crt
        os.mkdir(self._crt_build_subfolder)
        with tools.chdir(self._crt_build_subfolder):
            self._build_crt()
        # build winpthreads
        os.mkdir(self._winpthreads_build_subfolder)
        with tools.chdir(self._winpthreads_build_subfolder):
            self._build_winpthreads()
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
