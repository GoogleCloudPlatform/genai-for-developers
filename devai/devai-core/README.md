# Publishing

To publish on pypi follow the steps below

First update the version number in `setup.py`
Next, run the commands below

```sh
python3 -m venv venv
source venv/bin/activate

pip install build twine

rm -rf dist
rm -rf *.egg-info
python3 -m build .

twine upload --repository testpypi dist/* --verbose
```