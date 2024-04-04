%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

Name:           perl-MooseX-Clone
Version:        0.06
Release:        1%{?dist}
Summary:        Fine-grained cloning support for Moose objects
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/MooseX-Clone/
Source0:        MooseX-Clone-%{version}.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  perl >= 0:5.006
BuildRequires:  perl(Carp)
BuildRequires:  perl(Data::Visitor) >= 0.24
BuildRequires:  perl(Data::Visitor::Callback)
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(Hash::Util::FieldHash::Compat)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Moose)
BuildRequires:  perl(Moose::Role)
BuildRequires:  perl(Scalar::Util)
BuildRequires:  perl(Storable)
BuildRequires:  perl(Test::More) >= 0.88
BuildRequires:  perl(namespace::autoclean)
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
Requires:       perl(Carp)
Requires:       perl(Data::Visitor) >= 0.24
Requires:       perl(Data::Visitor::Callback)
Requires:       perl(Hash::Util::FieldHash::Compat)
Requires:       perl(Moose::Role)
Requires:       perl(Storable)
Requires:       perl(namespace::autoclean)

Provides:       perl(MooseX::Clone)

%description
Out of the box Moose only provides very barebones cloning support in order
to maximize flexibility.

%prep
%setup -q -n MooseX-Clone-%{version}

%build
%{__perl} Build.PL --installdirs=vendor
./Build

%install
rm -rf %{buildroot}

./Build install --destdir=%{buildroot} --create_packlist=0
find %{buildroot} -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} %{buildroot}/*

%check || :
./Build test

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CONTRIBUTING Changes LICENSE META.json README dist.ini
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Thu Apr 04 2024 Otto J Wittner <otto.wittner@sikt.no> 0.06-1
- Specfile autogenerated by cpanspec 1.78.
