# This Makefile is part of pisi
#
# global parameters
TITLE=		"PISI"
URL=		"https://projects.openmoko.org/projects/pisi/"
VERSION=	"0.4.3"

API_DOC_DIR=	apidoc/

# dependency parameters
DATEUTIL2.5=	"deps/python-dateutil-py2.5.tar.gz"
DATEUTIL2.6=	"deps/python-dateutil-py2.6.tar.gz"
VOBJECT2.5=	"deps/vobject-py2.5.tar.gz"
VOBJECT2.6=	"deps/vobject-py2.6.tar.gz"
PYTHONLDAP2.5=	"deps/python-ldap-py2.5.tar.gz"
PYTHONLDAP2.6=	"deps/python-ldap-py2.6.tar.gz"
PYTHONGDATA2.5=	"deps/gdata-py2.5.tar.gz"
PYTHONGDATA2.6=	"deps/gdata-py2.6.tar.gz"
PYTHONWEBDAV2.5=	"deps/python-webdav-py2.5.tar.gz"
PYTHONWEBDAV2.6=	"deps/python-webdav-py2.6.tar.gz"

# this generates API documentation in HTML format
# epydoc needs to be installed prior to usage - the epydoc program must be in your path environement.
api-docs:
	rm -rf $(API_DOC_DIR)	
	epydoc --inheritance listed -o $(API_DOC_DIR) -n $(TITLE)_$(VERSION) -u $(URL) *.py contacts/*.py events/*.py modules/*.py
	tar czf apidoc.tar.gz apidoc/

clean:
	rm -f *.pyc contacts/*.pyc events/*.pyc modules/*.pyc
	rm -rf build/template
	rm -f apidoc.tar.gz

# this whole thing is based on ipkg-build by Carl Worth
# http://cc.oulu.fi/~rantalai/freerunner/packaging/    
#
# make sure, you have provided all required up-to-date information in build/control before building a package
dist:	clean
	mkdir build/template
	mkdir build/template/CONTROL
	cp build/control build/template/CONTROL
	mkdir -p build/template/opt/pisi
	cp *.py COPYING README build/template/opt/pisi
	mkdir -p build/template/opt/pisi/contacts
	cp  contacts/*.py build/template/opt/pisi/contacts
	mkdir -p build/template/opt/pisi/events
	cp  events/*.py build/template/opt/pisi/events
	mkdir -p build/template/opt/pisi/modules
	cp  modules/*.py build/template/opt/pisi/modules
	mkdir -p build/template/opt/pisi/thirdparty
	cp  thirdparty/*.py build/template/opt/pisi/thirdparty
	mkdir build/template/bin
	ln -s /opt/pisi/pisi.py build/template/bin/pisi
	ln -s /opt/pisi/pisigui.py build/template/bin/pisigui
	mkdir -p build/template/home/root/.pisi
	cp conf build/template/home/root/.pisi/conf.default
	mkdir -p build/template/usr/share/applications
	cp build/pisi.desktop build/template/usr/share/applications
	mkdir -p build/template/usr/share/pixmaps
	cp build/pisi.png build/template/usr/share/pixmaps
	cd build && fakeroot ./ipkg-build template
	rm -rf build/template

sdist: clean
	tar czf build/pisi-src-$(VERSION).tar.gz *.py contacts/*.py events/*.py modules/*.py scripts/*.sql conf COPYING Makefile README

deps:	dep_dateutil dep_vobject dep_openldap dep_pythonldap dep_pythongdata dep_pythonwebdav
	

# creates an ipk for the correspondig dependency package
# make sure a binary distribution is located in the subfolder 'deps' (probably created by 'python setup.py bdist')
# make sure, you have provided all required up-to-date information in deps/control-XXX before building a package
dep_dateutil:
	mkdir -p deps/template/CONTROL
	cp deps/control-dateutil deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(DATEUTIL2.5)
	cd deps/template && tar xzf ../../$(DATEUTIL2.6)
	mkdir -p deps/template/usr/lib/python2.6/site-packages
	ln -s /usr/local/lib/python2.6/dist-packages/dateutil/ deps/template/usr/lib/python2.6/site-packages/dateutil
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_vobject:
	mkdir -p deps/template/CONTROL
	cp deps/control-vobject deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(VOBJECT2.5)
	cd deps/template && tar xzf ../../$(VOBJECT2.6)
	mkdir -p deps/template/usr/lib/python2.6/site-packages
	ln -s /usr/local/lib/python2.6/dist-packages/vobject/ deps/template/usr/lib/python2.6/site-packages/vobject
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_openldap:
	mkdir -p deps/template/CONTROL
	cp deps/control-openldap deps/template/CONTROL/control
	cp -r deps/ldap/usr deps/template
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_pythonldap:
	mkdir -p deps/template/CONTROL
	cp deps/control-pythonldap deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(PYTHONLDAP2.5)
	cd deps/template && tar xzf ../../$(PYTHONLDAP2.6)
	mkdir -p deps/template/usr/lib/python2.6/site-packages
	ln -s /usr/local/lib/python2.6/dist-packages/ldap deps/template/usr/lib/python2.6/site-packages/ldap
	cp deps/template/usr/local/lib/python2.6/dist-packages/*.p* deps/template/usr/lib/python2.6/site-packages/
	cp deps/template/usr/local/lib/python2.6/dist-packages/_ldap.so deps/template/usr/lib/python2.6/site-packages/
	ln -s /usr/lib/libssl.so.0.9.8 deps/template/usr/lib/libssl.so.0.9.7
	ln -s /usr/lib/libcrypto.so.0.9.8 deps/template/usr/lib/libcrypto.so.0.9.7
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_pythongdata:
	mkdir -p deps/template/CONTROL
	cp deps/control-pythongdata deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(PYTHONGDATA2.5)
	cd deps/template && tar xzf ../../$(PYTHONGDATA2.6)
	mkdir -p deps/template/usr/lib/python2.6/site-packages
	ln -s /usr/local/lib/python2.6/dist-packages/gdata deps/template/usr/lib/python2.6/site-packages/gdata
	ln -s /usr/local/lib/python2.6/dist-packages/atom deps/template/usr/lib/python2.6/site-packages/atom
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_pythonwebdav:
	mkdir -p deps/template/CONTROL
	cp deps/control-pythonwebdav deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(PYTHONWEBDAV2.5)
	cd deps/template && tar xzf ../../$(PYTHONWEBDAV2.6)
	mkdir -p deps/template/usr/lib/python2.6/site-packages
	ln -s /usr/local/lib/python2.6/dist-packages/webdav deps/template/usr/lib/python2.6/site-packages/webdav
	cp deps/template/usr/local/lib/python2.6/dist-packages/*.p* deps/template/usr/lib/python2.6/site-packages/
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

# PISI might be good for desktop use as well ...
# here go instructions for building Desktop packages
# 1. Ubuntu deb
# (install with: sudo apt-get python-vobject python-gdata && sudo dpkg -i pisi-$VERSION.deb)
dist_ubuntu:
	mkdir -p build/ubuntu/DEBIAN
	cp build/control-ubuntudeb build/ubuntu/DEBIAN/control
	mkdir -p build/ubuntu/usr/bin
	ln -s /opt/pisi/pisi.py build/ubuntu/usr/bin/pisi
	ln -s /opt/pisi/pisigui.py build/ubuntu/usr/bin/pisigui
	mkdir -p build/ubuntu/usr/share/applications
	cp build/pisi.desktop-ubuntu build/ubuntu/usr/share/applications/pisi.desktop
	mkdir -p build/ubuntu/usr/share/pixmaps
	cp build/pisi.png build/ubuntu/usr/share/pixmaps
	mkdir -p build/ubuntu/opt/pisi
	cp *.py COPYING README build/ubuntu/opt/pisi
	mkdir -p build/ubuntu/opt/pisi/contacts
	cp  contacts/*.py build/ubuntu/opt/pisi/contacts
	mkdir -p build/ubuntu/opt/pisi/events
	cp  events/*.py build/ubuntu/opt/pisi/events
	mkdir -p build/ubuntu/opt/pisi/modules
	cp  modules/*.py build/ubuntu/opt/pisi/modules
	mkdir -p build/ubuntu/opt/pisi/thirdparty
	cp  thirdparty/*.py build/ubuntu/opt/pisi/thirdparty
	cd build && dpkg --build ubuntu/ pisi-$(VERSION).deb
	rm -rf build/ubuntu
