default:
	@true

.PHONY: compiler
compiler:
	@poetry run python compiler/compiler.py

.PHONY: compressor
compressor:
	@poetry run python data_compressor/compressor.py
