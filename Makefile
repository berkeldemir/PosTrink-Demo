VENV_NAME = ENV
PYTHON = python3

.PHONY: all setup install clean fclean

all: install
	@echo "\nReady. Use 'source $(VENV_NAME)/bin/activate' command to activate the enviroment, and then run 'python main.py'.\n"

setup: $(VENV_NAME)

$(VENV_NAME):
	$(PYTHON) -m venv $(VENV_NAME)

install: setup
	./$(VENV_NAME)/bin/pip install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
	rm -f *.pyc
	rm -rf build dist .eggs *.egg-info

fclean: clean
	rm -rf $(VENV_NAME)
