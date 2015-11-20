VERSION := $(shell python3 -c "import batislib; print(batislib.__version__)")

.PHONY: docs batis

docs:
	make -C doc html

release: docs
	rm -rf build/batis
	mkdir -p build/batis
	# Copy files into a build directory
	cp --archive batis batislib install_resources batis_info build/batis/
	cp --archive doc/_build/html build/batis/html_docs
	# Bundle some PyPI packages Batis uses
	pip install --ignore-installed -t build/batis -r pypi_deps.txt
	# Remove cached .pyc files
	rm -rf build/batis/batislib/__pycache__ build/batis/batislib/*.pyc
	./batis pack build/batis -n batis -o batis-$(VERSION).app.tgz
	@echo "\"sha512\": \"$$(sha512sum batis-$(VERSION).app.tgz | cut -d' ' -f1)\""
