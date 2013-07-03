install:
	sudo mkdir /usr/local/gitless
	sudo cp -rf * /usr/local/gitless
	sudo ln /usr/local/gitless/gl /usr/local/bin/gl 
	sudo ln /usr/local/gitless/gl-track /usr/local/bin/gl-track
	sudo ln /usr/local/gitless/gl-untrack /usr/local/bin/gl-untrack
	sudo ln /usr/local/gitless/gl-status /usr/local/bin/gl-status
	sudo ln /usr/local/gitless/gl-diff /usr/local/bin/gl-diff
	sudo ln /usr/local/gitless/gl-commit /usr/local/bin/gl-commit
	sudo ln /usr/local/gitless/gl-branch /usr/local/bin/gl-branch
	sudo ln /usr/local/gitless/gl-checkout /usr/local/bin/gl-checkout
	sudo ln /usr/local/gitless/gl-rm /usr/local/bin/gl-rm
	sudo ln /usr/local/gitless/gl-merge /usr/local/bin/gl-merge
	sudo ln /usr/local/gitless/gl-resolve /usr/local/bin/gl-resolve
	sudo ln /usr/local/gitless/gl-rebase /usr/local/bin/gl-rebase
	sudo ln /usr/local/gitless/gl-remote /usr/local/bin/gl-remote
	sudo ln /usr/local/gitless/gl-push /usr/local/bin/gl-push
	sudo ln /usr/local/gitless/gl-init /usr/local/bin/gl-init
	sudo ln /usr/local/gitless/gl-history /usr/local/bin/gl-history

uninstall:
	-sudo rm -rf /usr/local/gitless
	-sudo rm /usr/local/bin/gl
	-sudo rm /usr/local/bin/gl-track
	-sudo rm /usr/local/bin/gl-untrack
	-sudo rm /usr/local/bin/gl-status
	-sudo rm /usr/local/bin/gl-diff
	-sudo rm /usr/local/bin/gl-commit
	-sudo rm /usr/local/bin/gl-branch
	-sudo rm /usr/local/bin/gl-checkout
	-sudo rm /usr/local/bin/gl-rm
	-sudo rm /usr/local/bin/gl-merge
	-sudo rm /usr/local/bin/gl-resolve
	-sudo rm /usr/local/bin/gl-rebase
	-sudo rm /usr/local/bin/gl-remote
	-sudo rm /usr/local/bin/gl-push
	-sudo rm /usr/local/bin/gl-init
	-sudo rm /usr/local/bin/gl-history
