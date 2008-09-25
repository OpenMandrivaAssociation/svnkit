%define gcj_support     0
%define section         free
%define eclipse_base	%{_libdir}/eclipse

Name:           svnkit
Version:        1.2.0
Release:        %mkrel 0.0.2.rc4
Epoch:          0
Summary:        Pure Java Subversion client library
Group:          Development/Java
License:        BSD-style
URL:            http://svnkit.com/
# XXX: This contains the sequence library, but I cannot find the
# XXX: original upstream source.
Source0:        http://svnkit.com/org.tmatesoft.svn_%{version}-rc4.src.zip
Source1:        svnkit-doc.tar.bz2
Source2:        svnkit-jsvn-script
Source3:        svnkit-jsvnadmin-script
Source4:        svnkit-jsvnlook-script  
Source5:        svnkit-jsvnsync-script
Patch0:         svnkit-1.1.4-no-javahl.patch
Requires:       trilead-ssh2
Requires:       jna
Requires:       svn-javahl
BuildRequires:  ant
BuildRequires:  java-rpmbuild >= 0:1.6
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel >= 0:1.4.2
BuildArch:      noarch
%endif
BuildRequires:  trilead-ssh2
BuildRequires:  jna
BuildRequires:  junit
BuildRequires:  svn-javahl
Obsoletes:      javasvn < %{epoch}:%{version}-%{release}
Provides:       javasvn = %{epoch}:%{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
SVNKit is a pure Java Subversion client library. You would like to use
SVNKit when you need to access or modify Subversion repository from
your Java application, be it a standalone program, plugin or web
application. Being a pure Java program, SVNKit doesn't need any
additional configuration or native binaries to work on any OS that runs
Java. On this site you will also find instructions on how to make
existing programs use SVNKit instead of native javahl bindings.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{name}-src-%{version}.4927
%setup -q -n %{name}-src-%{version}.4927 -T -D -a 1
%{_bindir}/find . -type d -name .svn | %{_bindir}/xargs -t %{__rm} -r
%remove_java_binaries

%{__ln_s} %{_javadir}/trilead-ssh2.jar contrib/trilead/trilead.jar
%{__ln_s} %{_javadir}/junit.jar contrib/junit/junit.jar
%{__ln_s} %{_javadir}/jna.jar contrib/jna/jna.jar

%build
export CLASSPATH=$(%{_bindir}/build-classpath svn-javahl jna trilead-ssh2)
export OPT_JAR_LIST=:
%{ant} build-library build-cli build-doc

#pushd svnkit-eclipse
#%{eclipse_base}/buildscripts/pdebuild -f org.tmatesoft.svnkit.feature \
#  -a "-DjavacTarget=1.6 -DjavacSource=1.6"
#popd

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a build/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
%{__cp} -a build/lib/%{name}-cli.jar %{buildroot}%{_javadir}/%{name}-cli-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a build/doc/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{__mkdir} %{buildroot}%{_bindir}
%{__cp} -a %{SOURCE2} %{buildroot}%{_bindir}/jsvn
%{__cp} -a %{SOURCE3} %{buildroot}%{_bindir}/jsvnadmin
%{__cp} -a %{SOURCE4} %{buildroot}%{_bindir}/jsvnlook
%{__cp} -a %{SOURCE5} %{buildroot}%{_bindir}/jsvnsync

pushd build/lib
%{__perl} -pi -e 's/\r$//g' README.txt SEQUENCE-LICENSE changelog.txt
popd

%{_bindir}/find doc/examples -type f -name '*.java' | %{_bindir}/xargs %{__perl} -pi -e 's/\r$//g'

%{gcj_compile}

%clean
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc build/lib/{README.txt,SEQUENCE-LICENSE,changelog.txt} doc/examples
%attr(0755,root,root) %{_bindir}/jsvn
%attr(0755,root,root) %{_bindir}/jsvnadmin
%attr(0755,root,root) %{_bindir}/jsvnlook
%attr(0755,root,root) %{_bindir}/jsvnsync
%{_javadir}/svnkit-%{version}.jar
%{_javadir}/svnkit.jar
%{_javadir}/svnkit-cli-%{version}.jar
%{_javadir}/svnkit-cli.jar
%{gcj_files}

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}
%doc %{_javadocdir}/%{name}-%{version}
