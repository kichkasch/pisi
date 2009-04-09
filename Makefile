# This Makefile is part of pisi
#
# global parameters
TITLE=		"PISI"
URL=		"https://projects.openmoko.org/projects/pisi/"
VERSION=	"0.1.2"

API_DOC_DIR=	apidoc/

# dependency parameters
DATEUTIL=	"deps/python-dateutil.tar.gz"
VOBJECT=	"deps/vobject.tar.gz"
PYTHONLDAP=	"deps/python-ldap.tar.gz"
PYTHONGDATA=	"deps/gdata.tar.gz"

# this generates API documentation in HTML format
# epydoc needs to be installed prior to usage - the epydoc program must be in your path environement.
api-docs:
	rm -rf $(API_DOC_DIR)	
	epydoc --inheritance listed -o $(API_DOC_DIR) -n $(TITLE) -u $(URL) *.py contacts/*.py events/*.py modules/*.py
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
	cp -r contacts events modules scripts build/template/opt/pisi
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

deps:	dep_dateutil dep_vobject dep_openldap dep_pythonldap dep_pythongdata
	

# creates an ipk for the correspondig dependency package
# make sure a binary distribution is located in the subfolder 'deps' (probably created by 'python setup.py bdist')
# make sure, you have provided all required up-to-date information in deps/control-XXX before building a package
dep_dateutil:
	mkdir deps/template
	mkdir deps/template/CONTROL
	cp deps/control-dateutil deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(DATEUTIL)
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_vobject:
	mkdir deps/template
	mkdir deps/template/CONTROL
	cp deps/control-vobject deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(VOBJECT)
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_openldap:
	mkdir deps/template
	mkdir deps/template/CONTROL
	cp deps/control-openldap deps/template/CONTROL/control
	cp -r deps/ldap/usr deps/template
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_pythonldap:
	mkdir deps/template
	mkdir deps/template/CONTROL
	cp deps/control-pythonldap deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(PYTHONLDAP)
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

dep_pythongdata:
	mkdir deps/template
	mkdir deps/template/CONTROL
	cp deps/control-pythongdata deps/template/CONTROL/control
	cd deps/template && tar xzf ../../$(PYTHONGDATA)
	cd deps && fakeroot ../build/ipkg-build template
	rm -rf deps/template

