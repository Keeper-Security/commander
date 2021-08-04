go2: tags
	# python3 -m pudb keeper.py
	python3 keeper.py

tags:
	ctags $$(find * -name '*.py' -print)

report:
	# pylint $$(find . -name '*.py' -print | sort -R) | ./desired-pylint-warnings
	pylint $$(find . -name '*.py' -print) || true

clean:
	rm -f tags
