#!/bin/sh

git for-each-ref --shell --format="ref=%(refname)" refs/heads | \
while read entry
do
	git pull
	git rm -r --cached development*
	git add -A
	git commit -am 'Removing ignored files'
done
git push