%global svn_revision     6888

%global eclipse_name     eclipse
%global eclipse_base     %{_libdir}/%{eclipse_name}
%global install_loc      %{_datadir}/eclipse/dropins
%global local_dropins    %{install_loc}/svnkit/eclipse
%global local_plugins    %{local_dropins}/plugins
%global local_features   %{local_dropins}/features
%global core_plugin_name org.tmatesoft.svnkit_%{version}
%global core_plugin_dir  %{local_plugins}/%{core_plugin_name}
%global jna_plugin_name  com.sun.jna_3.2.7
%global jna_plugin_dir   %{local_plugins}/%{jna_plugin_name}

Name:           svnkit
Version:        1.3.4
Release:        4
Summary:        Pure Java Subversion client library

Group:          Development/Java
# License located at http://svnkit.com/license.html
License:        TMate License and ASL 1.1
URL:            https://www.svnkit.com/
# original source located at: http://www.svnkit.com/org.tmatesoft.svn_%{version}.src.zip
# repackaged removing binary dependencies using:
# zip $FILE -d \*.jar
Source0:        org.tmatesoft.svn_%{version}.src-CLEAN.zip
Source1:        http://repo1.maven.org/maven2/org/tmatesoft/svnkit/svnkit/%{version}/svnkit-%{version}.pom 
Patch0:         svnkit-1.3.3-dependencies.patch
Patch1:         svnkit-1.3.3-ISVNStatusFileProvider.patch

BuildArch:      noarch

BuildRequires:          ant
BuildRequires:          jpackage-utils >= 0:1.6
BuildRequires:          eclipse-pde
BuildRequires:          svn-javahl >= 1.5
BuildRequires:          jna >= 3.0
BuildRequires:          trilead-ssh2 >= 213
BuildRequires:          sqljet
BuildRequires:          antlr3-java
Requires:               jna >= 3.0
Requires:               trilead-ssh2 >= 213
Requires:               sqljet
Obsoletes:              javasvn <= 1.1.0


%description
SVNKit is a pure Java Subversion client library. You would like to use SVNKit
when you need to access or modify Subversion repository from your Java
application, be it a standalone program, plugin or web application. Being a
pure Java program, SVNKit doesn't need any additional configuration or native
binaries to work on any OS that runs Java.

%package javahl
Summary:        Replacement for the native JavaHL API 
Group:          Development/Java
Requires:       svnkit = %{version}
Requires:       svn-javahl >= 1.5

%description javahl
SVNKit provides a replacement for the native JavaHL API - the SVNClient  class 
that does not use any native bindings. This SVNClient  also implements 
SVNClientInterface (org.tigris.subversion.javahl) as the native one 
but uses only the SVNKit library API (written in pure Java!).
If you have code written with using the native SVNClient class, 
you may simply replace that class with the new one provided by SVNKit. 

%package javadoc
Summary:        Javadoc for SVNKit
Group:          Development/Java

%description javadoc
Javadoc for SVNKit - Java Subversion client library.

%package -n eclipse-svnkit
Summary:        Eclipse feature for SVNKit
Group:          Development/Java
Requires:       svnkit = %{version}
Requires:       eclipse-platform

%description -n eclipse-svnkit
Eclipse feature for SVNKit - Java Subversion client library.


%prep
%setup -q -n %{name}-src-%{version}.%{svn_revision}
%patch0 -p0

# delete the jars that are in the archive
JAR_files=""
for j in $(find -name \*.jar); do
if [ ! -L $j ] ; then
JAR_files="$JAR_files $j"
fi
done
if [ ! -z "$JAR_files" ] ; then
echo "These JAR files should be deleted and symlinked to system JAR files: $JAR_files"
exit 1
fi
find contrib -name \*.jar -exec rm {} \;

# delete src packages for dependencies
rm contrib/trilead/trileadsrc.zip

# relinking dependencies
ln -s /usr/share/java/svn-javahl.jar contrib/javahl
ln -sf %{_javadir}/jna.jar contrib/jna/jna.jar
ln -sf %{_javadir}/trilead-ssh2.jar contrib/trilead/trilead.jar
ln -sf %{_javadir}/sqljet.jar contrib/sqljet/sqljet.jar
ln -sf %{_javadir}/antlr3-runtime.jar contrib/sqljet/antlr-runtime-3.1.3.jar

# fixing wrong-file-end-of-line-encoding warnings
sed -i 's/\r//' README.txt doc/javadoc/package-list
find doc/javadoc -name \*.html -exec sed -i 's/\r//' {} \;


%build
ECLIPSE_HOME=%{eclipse_base} ant

%install
rm -rf $RPM_BUILD_ROOT

# jar
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 build/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
install -m 644 build/lib/%{name}-javahl.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-javahl.jar

install -Dm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-svnkit.pom
%add_to_maven_depmap org.tmatesoft.svnkit %{name} %{version} JPP %{name}

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr doc/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# eclipse
mkdir -p $RPM_BUILD_ROOT%{local_dropins}
cp -R build/eclipse/features $RPM_BUILD_ROOT%{local_dropins}

# extracting plugin jars
mkdir $RPM_BUILD_ROOT%{local_plugins}
unzip build/eclipse/site/plugins/%{jna_plugin_name}.jar -d $RPM_BUILD_ROOT%{jna_plugin_dir}
unzip build/eclipse/site/plugins/%{core_plugin_name}.jar -d $RPM_BUILD_ROOT%{core_plugin_dir}
 
# removing plugin internal jars and sources
rm -f $RPM_BUILD_ROOT%{jna_plugin_dir}/jna.jar
rm -fR $RPM_BUILD_ROOT%{jna_plugin_dir}/com
rm -f $RPM_BUILD_ROOT%{core_plugin_dir}/{svnkitsrc.zip,trilead.jar,svnkit.jar,svnkit-javahl.jar,sqljet.1.0.1.jar,antlr-runtime-3.1.3.jar}

# We need to setup the symlink because the ant copy task doesn't preserve symlinks
# TODO file a bug about this
ln -s %{_javadir}/svn-javahl.jar $RPM_BUILD_ROOT%{core_plugin_dir}
ln -s %{_javadir}/trilead-ssh2.jar $RPM_BUILD_ROOT%{core_plugin_dir}/trilead.jar
ln -s %{_javadir}/svnkit.jar $RPM_BUILD_ROOT%{core_plugin_dir}
ln -s %{_javadir}/jna.jar $RPM_BUILD_ROOT%{jna_plugin_dir}
ln -s %{_javadir}/sqljet.jar $RPM_BUILD_ROOT%{core_plugin_dir}/sqljet.1.0.1.jar
ln -s %{_javadir}/antlr3.jar $RPM_BUILD_ROOT%{core_plugin_dir}/antlr-runtime-3.1.3.jar


%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root)
%{_mavenpomdir}
%{_mavendepmapdir}
%{_javadir}/%{name}.jar
%doc README.txt changelog.txt

%files javahl
%defattr(-,root,root)
%{_javadir}/%{name}-javahl.jar

%files -n eclipse-svnkit
%defattr(-,root,root,-)
%{install_loc}/svnkit


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}


