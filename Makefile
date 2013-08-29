
default:

clean:
	find . -type f -name '*.pyc' -print0 | xargs -0 rm -f -- 
	rm -rf *.egg-info
