[![CodeFactor](https://www.codefactor.io/repository/github/andrewsultan/freqml/badge/master?s=a80aec3f2511c18cec45afbe37ad9e5bed0baa84)](https://www.codefactor.io/repository/github/andrewsultan/freqml/overview/master)
# Quick start
```bash
git clone --recurse-submodules https://github.com/AndrewSultan/freqml.git
cd freqml
# ./setup.sh in the future
git checkout master
python3 -m venv .env
source .env/bin/activate
python3 -m pip install --upgrade pip
pip install -e .
pip install ipykernel
ipython kernel install --user --name=freqml
pip install swifter
```
