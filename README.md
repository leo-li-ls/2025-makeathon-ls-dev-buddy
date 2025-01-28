# LS Dev Buddy

## Install dependencies

This introduction is for macOS, and only work with Python 3.11

1. install python 3.11

    ```bash
    brew install python@3.11
    ```

2. Install the following dependencies:

    ```bash
    rm -rf myenv
    python3.11 -m venv myenv
    source myenv/bin/activate
    python --version  # Should say 3.11.x

    pip install --upgrade pip
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements.txt
    pip install "unstructured[md]"
    ```

## Create database

Create the Chroma DB.

```python
python src/create_database.py
```

## Query the database

Query the Chroma DB.

```python
python src/query_data.py "How does Alice meet the Mad Hatter?"
```
