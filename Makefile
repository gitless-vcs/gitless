build: clean
	./build.py bin

clean:
	-rm -rf bin

install: uninstall
	mkdir /usr/local/gitless
	cp -rf bin /usr/local/gitless
	ln -s /usr/local/gitless/bin/gl /usr/local/bin/gl 

uninstall:
	-rm -rf /usr/local/gitless
	-rm /usr/local/bin/gl

debug-install: uninstall
	ln -s ${CURDIR}/gl.py /usr/local/bin/gl
