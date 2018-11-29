#!/bin/sh

for branch in $(git for-each-ref --format='%(refname)' refs/heads/); do
	git checkout "$branch"
	git pull
	git rm -r --cached development*
	git add -A
	git commit -am 'Removing ignored files'
done
git push
