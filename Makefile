SRC_DIR=src

.PHONY: typecheck go

typecheck:
	@python -m mypy $(SRC_DIR) --pretty --follow-imports skip || true

go:
	@PYTHONPATH=$(SRC_DIR) python -B -m $(word 2, $(MAKECMDGOALS))

%:
	@: