%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

Name:           perl-Test-Deep-JSON
Version:        0.05
Release:        1%{?dist}
Summary:        Compare JSON with Test::Deep
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/Test-Deep-JSON/
Source0:        Test-Deep-JSON-%{version}.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  perl >= 0:5.008001
BuildRequires:  perl(Exporter::Lite)
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.59
BuildRequires:  perl(JSON::MaybeXS)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Test::Deep)
BuildRequires:  perl(Test::More)
BuildRequires:  perl(Test::Tester)
Requires:       perl(Exporter::Lite)
Requires:       perl(JSON::MaybeXS)
Requires:       perl(Test::Deep)

Provides:       perl(Test::Deep::JSON)

%description
Test::Deep::JSON provides the json($expected) function to expect that
target can be parsed as a JSON string and matches (by cmp_deeply) with
$expected.

%prep
%setup -q -n Test-Deep-JSON-%{version}

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
%doc Changes LICENSE META.json README.md cpanfile minil.toml
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Thu Apr 11 2024 Otto J Wittner <otto.wittner@sikt.no> 0.05-1
- Specfile autogenerated by cpanspec 1.78.
