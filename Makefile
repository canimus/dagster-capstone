black: # Format code
	@black cuallee
	@black test

clean: # Remove workspace files
	@find . -name "__pycache__" -exec rm -rf {} +
	@rm -rf ./.pytest_cache
	@rm -rf ./htmlcov
	@rm -rf dist/
	@rm -rf capstone/capstone.egg-info/
	@rm -rf capstone.egg-info/
	@rm -rf build/
	@rm -rf __blobstorage__
	@rm -rf .mypy_cache
	@rm -rf .coverage
	@rm -rf .DS_Store

	@rm -rf spark-warehouse
	@python -c "print('Cleaning: 👌')"

commit: # Run pre-commit
	@pre-commit run --all-files
