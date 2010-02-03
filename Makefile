# This Makefile is part of pisi
#
# global parameters
TITLE=		"PISI"
URL=		"http://freshmeat.net/projects/pisiom"
VERSION=	"0.5"
PACKAGE_NAME =pisi

API_DOC_DIR=	apidoc/

# for UBUNTU Launchpad upload of deb package
PGP_KEYID ="1B09FB51"
BUILD_VERSION = "0ubuntu3"


# this generates API documentation in HTML format
# epydoc needs to be installed prior to usage - the epydoc program must be in your path environement.
api-docs:
	rm -rf $(API_DOC_DIR)	
	epydoc --inheritance listed -o $(API_DOC_DIR) -n $(TITLE)_$(VERSION) -u $(URL) *.py contacts/*.py events/*.py modules/*.py thirdparty/conduit/*.py
	tar czf apidoc.tar.gz apidoc/

clean:
	rm -f *.pyc contacts/*.pyc events/*.pyc modules/*.pyc
	rm -rf build/template
	rm -f apidoc.tar.gz
	rm -f build/$(PACKAGE_NAME)-$(VERSION).orig.tar.gz
	rm -rf build/$(PACKAGE_NAME)-$(VERSION)
	rm -rf build/ubuntu
	rm -f build/*ppa.upload

# this whole thing is based on ipkg-build by Carl Worth
# http://cc.oulu.fi/~rantalai/freerunner/packaging/    
#
# make sure, you have provided all required up-to-date information in build/control before building a package
#
# please note: these packages are only for temporary testing; proper packages are now build by SHR build environment
# using source packages (see also http://wiki.github.com/kichkasch/pisi/instructions-for-releasing-a-new-version)
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
	mkdir -p build/template/opt/pisi/thirdparty/conduit
	cp  thirdparty/conduit/*.py build/template/opt/pisi/thirdparty/conduit
	mkdir build/template/bin
	ln -s /opt/pisi/pisi.py build/template/bin/pisi
	ln -s /opt/pisi/pisigui.py build/template/bin/pisigui
	mkdir -p build/template/usr/local/doc/pisi
	cp conf.example build/template/usr/local/doc/pisi/conf.example
	mkdir -p build/template/usr/share/applications
	cp build/pisi.desktop build/template/usr/share/applications
	mkdir -p build/template/usr/share/pixmaps
	cp build/pisi.png build/template/usr/share/pixmaps
	cd build && fakeroot ./ipkg-build template
	rm -rf build/template

sdist: clean
	tar cf build/tmp.tar *.py contacts/*.py events/*.py modules/*.py scripts/*.sql thirdparty/*.py thirdparty/conduit/*.py conf.example COPYING README build/$(PACKAGE_NAME).desktop build/$(PACKAGE_NAME).png
	mkdir $(PACKAGE_NAME)-$(VERSION)
	(cd $(PACKAGE_NAME)-$(VERSION) && tar -xf ../build/tmp.tar)
	rm build/tmp.tar
	tar czf build/$(PACKAGE_NAME)-src-$(VERSION).tar.gz $(PACKAGE_NAME)-$(VERSION)
	rm -rf $(PACKAGE_NAME)-$(VERSION)


# PISI might be good for desktop use as well ...
# here go instructions for building Desktop packages
# 1. Ubuntu deb

# All up-to-date information must be applied to sub dir build/debian in advance
sdist_ubuntu: sdist
	export DEBFULLNAME="Michael Pilgermann"
	export DEBEMAIL="kichkasch@gmx.de"
	cp build/$(PACKAGE_NAME)-src-$(VERSION).tar.gz build/$(PACKAGE_NAME)-$(VERSION).orig.tar.gz
	(cd build && tar -xzf $(PACKAGE_NAME)-$(VERSION).orig.tar.gz)
	cp -r build/debian build/$(PACKAGE_NAME)-$(VERSION)/
	cp README build/$(PACKAGE_NAME)-$(VERSION)/debian/README.Debian
	dch -m -c build/$(PACKAGE_NAME)-$(VERSION)/debian/changelog
	(cd build/$(PACKAGE_NAME)-$(VERSION)/ && dpkg-buildpackage -S -k$(PGP_KEYID))
	
ppa_upload: sdist_ubuntu
	(cd build/ && dput kichkasch-ppa $(PACKAGE_NAME)_$(VERSION)-$(BUILD_VERSION)_source.changes)
