
default: sdist

sdist:
	python setup.py sdist

register: checkmetadata
	python setup.py register

upload: checkmetadata
	python setup.py sdist upload --sign -r https://pypi.python.org/pypi

checkmetadata:
	python setup.py check -s --restructuredtext

clean:
	find . -type f -name '*.pyc' -print0 | xargs -0 rm -f -- 
	rm -rf *.egg-info
	rm -rf dist/
