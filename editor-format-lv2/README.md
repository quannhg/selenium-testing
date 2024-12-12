## Prerequisites
chromedriver
## How to run
```bash
# python3 -m venv venv # create virtual enviroment if needed
source venv/bin/activate # enter virtual environment
pip3 install -r requirements.txt # install dependencies
pytest # run all the tests
# pytest --headed # add headed flag if you want to see browser runnings
# pytest -n <number parallel workers> # add -n flag if you want to run tests parallel
# pytest -s # add -s if you want see the log
```
## About data
- Each row represents an execution of the test case.
- To skip one row, just add the coloumn `_skip` and set value for that row is `True`.