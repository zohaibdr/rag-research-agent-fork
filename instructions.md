### Make it Installable

This project uses **[PEP 621](https://peps.python.org/pep-0621/)**-compatible `pyproject.toml` for packaging.  
To install in **editable mode**, run the following command from the root folder:

```bash
pip install -e .
```

This will install the project along with its dependencies, and allow changes in the src/ code to reflect immediately without reinstalling.

### To Run the Agent:

Ensure you're in the project root directory, then run:
```bash
python src/invoke_graph.py
```