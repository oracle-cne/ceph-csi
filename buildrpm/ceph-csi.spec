{{{$version := printf "%s.%s.%s" .major .minor .patch }}}
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global app_name ceph-csi
%global app_version {{{$version}}}
%global oracle_release_version 1
%global golang_version 1.22.7
%global _buildhost	build-ol%{?oraclelinux}-%{?_arch}.oracle.com

Name:               %{app_name}
Version:            %{app_version}
Release:            %{oracle_release_version}%{?dist}
Summary:            A Kubernetes CSI driver for Ceph
License:            Apache 2.0
URL:                https://github.com/ceph/ceph-csi
Source:             %{name}-%{version}.tar.bz2
Vendor:             Oracle America
Group:              System/Management
BuildRequires:      golang >= %{golang_version}
BuildRequires:      librados-devel
BuildRequires:      librbd-devel
{{{- if semverCompare ">=3.10.0" $version }}}
BuildRequires:      libcephfs-devel
{{{- end }}}
BuildRequires:      make
BuildRequires:      git
BuildRequires:      /usr/bin/cc
Requires:           librados2 >= 14.2.0
Requires:           librbd1 >= 14.2.0

%description
A driver for the Kubernetes CSI using Ceph.  Ceph-csi enables the use of
Kubernetes APIs to manage Ceph storage.

%prep
export CGO_ENABLED=1
%setup -n %{name}-%{version}

%build
make cephcsi LDFLAGS="-X main.version={{{$app_version}}}"

%install
install -D -p -m 0555 _output/cephcsi %{buildroot}/usr/local/bin/cephcsi

%files
%license LICENSE THIRD_PARTY_LICENSES.txt
/usr/local/bin/cephcsi

%clean
make clean

%changelog
* {{{.changelog_timestamp}}} - {{{$version}}}-1
- Added Oracle Specific Build Files for ceph-csi
