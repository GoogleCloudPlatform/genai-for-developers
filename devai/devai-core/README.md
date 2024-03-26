# Publishing

python3 -m venv venv
source venv/bin/activate

pip install build twine

rm -rf dist
rm -rf *.egg-info
python3 -m build .

twine upload --repository testpypi dist/* --verbose
