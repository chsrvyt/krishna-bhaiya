.PHONY: run test

run:
	python agent/run.py --brief brief.yaml --max-accounts 3 --contacts-per-account 1

test:
	python -m pytest -q
