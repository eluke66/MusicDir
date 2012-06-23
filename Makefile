VERSION = 1.3
APPS = /usr/local/apps
MDIR = $(APPS)/MusicDir_$(VERSION)


export: $(MDIR)
	cp *.py BUGS cmd README full.db $(MDIR)

tarball:	md.tar


$(MDIR):
	mkdir -p $(MDIR)

clean:
	rm *.pyc *~ svn-commit*

md.tar:	*.py
	tar cf $@ *.py BUGS cmd README Makefile