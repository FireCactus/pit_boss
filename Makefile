SRC_DIR=src

.PHONY: typecheck go

typecheck:
	@python -m mypy $(SRC_DIR) --cache-dir=/dev/null --follow-imports skip || true

go:
	@PYTHONPATH=$(SRC_DIR) python -B -m $(word 2, $(MAKECMDGOALS))

%:
	@: