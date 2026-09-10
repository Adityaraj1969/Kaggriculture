.PHONY: test benchmark package lint clean

test:
	python -m unittest discover -s tests -p "test_*.py"

benchmark:
	python tools/benchmark.py --seeds 1,2,3,4,5,42,100,256,777,999

league:
	python tools/evaluate_league.py --seeds 1,2,3,4,5

package:
	python tools/package_submission.py

lint:
	ruff check .
	mypy main.py src/

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__
