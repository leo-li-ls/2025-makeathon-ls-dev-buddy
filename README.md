# LS Dev Buddy

## Install dependencies

This introduction is for macOS, and only work with Python 3.13

1. install python 3.13

    ```bash
    brew install python@3.13
    ```

2. Install the following dependencies:

    ```bash
    rm -rf myenv
    python3.13 -m venv myenv
    source myenv/bin/activate
    pip install -r requirements.txt
    pip install "unstructured[md]"
    ```

## Create database

Create the Chroma DB.

```python
python create_database.py
```

## Query the database

Query the Chroma DB.

```python
python query_data.py "How does Alice meet the Mad Hatter?"
```
