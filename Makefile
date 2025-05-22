SRC_DIR=src

typecheck:
	python -m mypy $(SRC_DIR) --cache-dir=/dev/null

.PHONY: typecheck