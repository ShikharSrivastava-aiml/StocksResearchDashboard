# The application is currently hosted on google cloud vm http://34.138.213.172:8501/   
# The service registry and it's health is currently hosted on http://34.138.213.172:8500/


## To run the application enter the following commands in terminal:

git clone https://github.com/ShikharSrivastava-aiml/StockResearchDashboard.git

pip3 install -r requirements.txt

python3 -m streamlit run app.py

## Running Tests
Running tests creates pycache files. There are 39 tests all in the tests/ directory.
For more info about the tests visit our project documentation or look at the comments in test files.
To run the test suite, use the following command:

python -m pytest

