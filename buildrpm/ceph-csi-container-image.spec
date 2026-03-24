
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%{!?registry_url: %global registry_url container-registry.oracle.com/olcne}
%{!?registry: %global registry container-registry.oracle.com/olcne}

%global _name           ceph-csi	
%global _buildhost	build-ol%{?oraclelinux}-%{?_arch}.oracle.com
%ifarch %{arm} arm64 aarch64
%global arch aarch64
%global custom_arch arm64
%else
%global arch x86_64
%global custom_arch amd64
%endif
%global ceph_version "19.2.1"


Name:           %{_name}-container-image
Version:        3.16.0
Release:        1%{?dist}
Summary:        Ceph CSI container image
License:        Apache-2.0
Group:          System/Management
Url:            https://github.com/ceph/ceph-csi
Source:         %{name}-%{version}.tar.bz2

BuildRequires: python36
BuildRequires: podman

%description
Ceph CSI container image

%prep
%setup -q -n %{name}-%{version}

%build
# NOTE: Make sure ceph image built before this
%global ceph_tag container-registry.oracle.com/olcne/ceph:v%{ceph_version}
if [[ $( podman pull %{ceph_tag} ) && \
      $( podman inspect -t image -f "{{.Architecture}}"  %{ceph_tag} ) = %{custom_arch} ]];then
     echo "Using ceph image from ocr"
elif [[ $( podman pull %{registry_url}/ceph:v%{ceph_version} ) && \
        $( podman inspect -t image -f "{{.Architecture}}"  %{registry_url}/ceph:v%{ceph_version} ) = %{custom_arch} ]];then
    podman rmi -f %{ceph_tag}
    podman tag %{registry_url}/ceph:v%{ceph_version} %{ceph_tag}
else
     echo "Ceph:v%{ceph_version} doesn't exist"
     exit 1
fi

%global cephcsi_rpm %{_name}-%{version}-%{release}.%{arch}
%global cephcsi_tag %{registry}/cephcsi:v%{version}

dnf clean all && \
  yumdownloader --destdir=${PWD}/rpms %{cephcsi_rpm}
podman build \
    --build-arg BASE_IMAGE=%{ceph_tag} \
    -t %{cephcsi_tag} -f ./olm/builds/Dockerfile.csi .
podman save -o %{_name}.tar %{cephcsi_tag}

%install
%__install -D -m 644 %{_name}.tar %{buildroot}/usr/local/share/olcne/%{_name}.tar

%files
%license LICENSE
/usr/local/share/olcne/%{_name}.tar

%changelog
* Tue Mar 24 2026 Oracle Cloud Native Environment Authors <noreply@oracle.com> - 3.16.0-1
- Added Oracle Specific Build Files for ceph-csi
