# Warning: This package is synchronized with Fedora!
%define _disable_lto %nil

%define major 1
%define api 1
%define gir_major 1.0
%define libname %mklibname ostree %{major}
%define gir_name %mklibname ostree-gir %{gir_major}
%define develname %mklibname -d ostree

Summary:	Tool for managing bootable, immutable filesystem trees
Name:		ostree
Version:	2020.2
Release:	1
#VCS: git:git://git.gnome.org/ostree
Source0:	https://github.com/ostreedev/ostree/releases/download/v%{version}/libostree-%{version}.tar.xz
Source1:	91-ostree.preset
License:	LGPLv2+
URL:		https://ostree.readthedocs.io/en/latest/

BuildRequires:	git
# We always run autogen.sh
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	bison
# For docs
BuildRequires:	gtk-doc
# Core requirements
BuildRequires:	pkgconfig(libsoup-2.4)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	attr-devel
# Extras
BuildRequires:	pkgconfig(mount)
BuildRequires:	pkgconfig(libarchive)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(mount)
BuildRequires:	pkgconfig(fuse)
BuildRequires:	pkgconfig(e2p)
BuildRequires:	libcap-devel
BuildRequires:	gpgme-devel
BuildRequires:	libassuan-devel
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-macros
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	dracut

# Runtime requirements
Requires:	dracut
Requires:	gnupg2
Requires:	systemd

%description
OSTree is a tool for managing bootable, immutable, versioned
filesystem trees. While it takes over some of the roles of tradtional
"package managers" like dpkg and rpm, it is not a package system; nor
is it a tool for managing full disk images. Instead, it sits between
those levels, offering a blend of the advantages (and disadvantages)
of both.

%package -n %{libname}
Summary:	Tool for managing bootable, immutable filesystem trees
Group:		System/Libraries

%description -n %{libname}
OSTree is a tool for managing bootable, immutable, versioned
filesystem trees. While it takes over some of the roles of tradtional
"package managers" like dpkg and rpm, it is not a package system; nor
is it a tool for managing full disk images. Instead, it sits between
those levels, offering a blend of the advantages (and disadvantages)
of both.

%package -n %{develname}
Summary:	Development headers for %{name}
Group:		System/Libraries
Requires:	%{name} =  %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{gir_name} = %{EVRD}

%description -n %{develname}
This package includes the header files for the %{name} library.

%package -n %{gir_name}
Summary:	GObject Introspection interface description for %{name}
Group:		System/Libraries
Requires:	%{libname} = %{EVRD}

%description -n %{gir_name}
GObject Introspection interface description for %{name}.

%ifnarch s390 s390x %{arm}
%package	grub2
Summary:	GRUB2 integration for OSTree
%ifnarch aarch64
Requires:	grub2
%else
Requires:	grub2-efi
%endif

%description grub2
GRUB2 integration for OSTree
%endif

%prep
%autosetup -n libostree-%{version} -p1

%build
env NOCONFIGURE=1 ./autogen.sh
%configure \
    --disable-silent-rules \
    --enable-gtk-doc \
    --with-curl \
    --with-openssl \
    --with-dracut=yesbutnoconf

# https://gitlab.gnome.org/GNOME/gobject-introspection/issues/280
sed -i 's!-fvisibility=hidden!-fvisibility=default!g' Makefile.in Makefile-libostree.am

# HACK
sed -i s'!\\{libdir\\}!%{_libdir}!g' Makefile
%make_build

%install
%make_install
find %{buildroot} -name '*.la' -delete
install -D -m 0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/systemd/system-preset/91-ostree.preset

%files
%{_bindir}/ostree
%{_bindir}/rofiles-fuse
%{_datadir}/ostree/trusted.gpg.d
%{_sysconfdir}/ostree
%dir %{_prefix}/lib/dracut/modules.d/98ostree
%{_unitdir}/ostree*.service
%{_unitdir}/ostree*.path
%{_prefix}/lib/dracut/modules.d/98ostree/*
%{_mandir}/man*/*.*
%{_prefix}/lib/systemd/system-preset/91-ostree.preset
%exclude %{_sysconfdir}/grub.d/*ostree
%exclude %{_libexecdir}/libostree/grub2*
%{_prefix}/lib/ostree/ostree-prepare-root
%{_prefix}/lib/ostree/ostree-remount
/lib/systemd/system-generators/ostree-system-generator
%{_prefix}/lib/tmpfiles.d/ostree-tmpfiles.conf
%{_datadir}/bash-completion/completions/ostree
%{_libexecdir}/libostree/*

%files -n %{libname}
%{_libdir}/lib%{name}-%{api}.so.%{major}*

%files -n %{develname}
%doc COPYING
%doc README.md
%{_libdir}/lib*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_datadir}/gtk-doc/html/ostree
%{_datadir}/gir-1.0/OSTree-1.0.gir

%files -n %{gir_name}
%{_libdir}/girepository-1.0/OSTree-%{gir_major}.typelib

%ifnarch s390 s390x %{arm}
%files grub2
%{_sysconfdir}/grub.d/*ostree
%{_libexecdir}/libostree/grub2*
%endif
