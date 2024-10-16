%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

Name:           perl-Net-AMQP
Version:        0.06
Release:        1%{?dist}
Summary:        Advanced Message Queue Protocol (de)serialization and representation
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/Net-AMQP/
Source0:        Net-AMQP-%{version}.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  perl(Class::Accessor)
BuildRequires:  perl(Class::Data::Inheritable)
BuildRequires:  perl(File::Temp) >= 0.19
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Scalar::Util)
BuildRequires:  perl(Test::Deep)
BuildRequires:  perl(Test::More) >= 0.88
BuildRequires:  perl(XML::LibXML)
Requires:       perl(Class::Accessor)
Requires:       perl(Class::Data::Inheritable)
Requires:       perl(Scalar::Util)
Requires:       perl(XML::LibXML)

Provides:       perl(Net::AMQP)
Provides:       perl(Net::AMQP::Protocol)
Provides:       perl(Net::AMQP::Frame)
Provides:       perl(Net::AMQP::Value)
Provides:       perl(Net::AMQP::Common)
Provides:       perl(Net::AMQP::Frame::Trace)
Provides:       perl(Net::AMQP::Frame::OOBBody)
Provides:       perl(Net::AMQP::Frame::OOBHeader)
Provides:       perl(Net::AMQP::Frame::Heartbeat)
Provides:       perl(Net::AMQP::Frame::OOBMethod)
Provides:       perl(Net::AMQP::Frame::Body)
Provides:       perl(Net::AMQP::Frame::Method)
Provides:       perl(Net::AMQP::Frame::Header)
Provides:       perl(Net::AMQP::Protocol::Base)
Provides:       perl(Net::AMQP::Protocol::v0_8)

%description
This module implements the frame (de)serialization and representation of
the Advanced Message Queue Protocol (http://www.amqp.org/). It is to be
used in conjunction with client or server software that does the actual
TCP/IP communication.

%prep
%setup -q -n Net-AMQP-%{version}

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
%doc CHANGES LICENSE META.json README eg spec
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Fri Apr 05 2024 Otto J Wittner <otto.wittner@sikt.no> 0.06-1
- Specfile autogenerated by cpanspec 1.78.
