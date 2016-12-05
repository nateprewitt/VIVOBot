init:
	pip install -r requirements.txt

test:
	py.test tests

coverage:
	py.test --verbose --cov-report term --cov=vivobot tests
