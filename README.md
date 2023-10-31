# dai


Venv Commands

```sh
python3 -m venv venv
. venv/bin/activate
deactivate
```

Dependencies
```sh
pip install click
pip install google-cloud-aiplatform
pip install google-cloud-discoveryengine

pip freeze > requirements.txt

pip install -r requirements.txt
```

Run the app from source
```sh
python hello.py
```

Install the app
```sh
pip install --editable .
```

Run the installed app
```sh
dai ai
```

Uninstall the app
```sh
python setup.py develop -u
```

Use the app
```sh
cd gcloudai
python gcloudai/hello.py query
```

Docker

```sh
docker build -t dai-img .
docker run -it dai-img
dai ai
```