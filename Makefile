build:
	./build.py bin

clean:
	-rm -rf bin

install:
	mkdir /usr/local/gitless
	cp -rf bin /usr/local/gitless
	ln -s /usr/local/gitless/bin/gl /usr/local/bin/gl 
	ln -s /usr/local/gitless/bin/gl-track /usr/local/bin/gl-track
	ln -s /usr/local/gitless/bin/gl-untrack /usr/local/bin/gl-untrack
	ln -s /usr/local/gitless/bin/gl-status /usr/local/bin/gl-status
	ln -s /usr/local/gitless/bin/gl-diff /usr/local/bin/gl-diff
	ln -s /usr/local/gitless/bin/gl-commit /usr/local/bin/gl-commit
	ln -s /usr/local/gitless/bin/gl-branch /usr/local/bin/gl-branch
	ln -s /usr/local/gitless/bin/gl-checkout /usr/local/bin/gl-checkout
	ln -s /usr/local/gitless/bin/gl-rm /usr/local/bin/gl-rm
	ln -s /usr/local/gitless/bin/gl-merge /usr/local/bin/gl-merge
	ln -s /usr/local/gitless/bin/gl-resolve /usr/local/bin/gl-resolve
	ln -s /usr/local/gitless/bin/gl-rebase /usr/local/bin/gl-rebase
	ln -s /usr/local/gitless/bin/gl-remote /usr/local/bin/gl-remote
	ln -s /usr/local/gitless/bin/gl-push /usr/local/bin/gl-push
	ln -s /usr/local/gitless/bin/gl-init /usr/local/bin/gl-init
	ln -s /usr/local/gitless/bin/gl-history /usr/local/bin/gl-history

uninstall:
	-rm -rf /usr/local/gitless
	-rm /usr/local/bin/gl
	-rm /usr/local/bin/gl-track
	-rm /usr/local/bin/gl-untrack
	-rm /usr/local/bin/gl-status
	-rm /usr/local/bin/gl-diff
	-rm /usr/local/bin/gl-commit
	-rm /usr/local/bin/gl-branch
	-rm /usr/local/bin/gl-checkout
	-rm /usr/local/bin/gl-rm
	-rm /usr/local/bin/gl-merge
	-rm /usr/local/bin/gl-resolve
	-rm /usr/local/bin/gl-rebase
	-rm /usr/local/bin/gl-remote
	-rm /usr/local/bin/gl-push
	-rm /usr/local/bin/gl-init
	-rm /usr/local/bin/gl-history
