HTML_FILES:= $(wildcard doc/*.html)

clean:
	find -name "*.pyc" -type f -delete
	find -name "__pycache__" -type d -delete
	-rm -f "README.html"
	-rm -f "$(HTML_FILES)"
