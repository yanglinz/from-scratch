default:
	@true

.PHONY: compiler
compiler:
	@poetry run python compiler/compiler.py

.PHONY: compressor
compressor:
	@poetry run python data_compressor/compressor.py

.PHONY: editor
editor:
	@poetry run python text_editor/editor.py
