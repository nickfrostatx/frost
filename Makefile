test:
	py.test -vv --pep8 --cov=frost --cov-report=term-missing frost/ tests/

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
