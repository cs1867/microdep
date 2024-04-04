%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

Name:           perl-Geometry-Primitive
Version:        0.24
Release:        1%{?dist}
Summary:        Geometry::Primitive Perl module
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/Geometry-Primitive/
Source0:        Geometry-Primitive-%{version}.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  perl(Check::ISA) >= 0.04
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(JSON::Any) >= 1.22
BuildRequires:  perl(Math::Complex) >= 1.56
BuildRequires:  perl(Moose) >= 0.92
BuildRequires:  perl(MooseX::Clone) >= 0.04
BuildRequires:  perl(MooseX::Storage) >= 0.23
BuildRequires:  perl(Test::More)
Requires:       perl(Check::ISA) >= 0.04
Requires:       perl(Math::Complex) >= 1.56
Requires:       perl(Moose) >= 0.92
Requires:       perl(MooseX::Clone) >= 0.04
Requires:       perl(MooseX::Storage) >= 0.23

Provides:       perl(Geometry::Primitive)

%description
Geometry::Primitive is a device and library agnostic system for
representing geometric entities such as points, lines and shapes.  It
provides simple objects and many convenience methods you would expect from
a simple geometry library.

%prep
%setup -q -n Geometry-Primitive-%{version}

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}

%install
rm -rf %{buildroot}

make pure_install PERL_INSTALL_ROOT=%{buildroot}

find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} %{buildroot}/*

%check || :
make test

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc Changes README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Thu Apr 04 2024 Otto J Wittner <otto.wittner@sikt.no> 0.24-1
- Specfile autogenerated by cpanspec 1.78.
