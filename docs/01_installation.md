# INSTALLATION

[⬅️ Home](../README.md)
___

The installation procedure is the same for all platforms. The only requirement
is Python 3.11. The recommended way to install is using `pip`:

## Install from PyPI

```bash
python3.11 -m pip install pytorch-lightning
```

## Install from source

```bash
git clone https://github.com/sgelias/gene-connector-cli.git
cd gene-connector-cli
python3.11 -m pip install .
```

## Install from source (editable)

```bash
python3.11 -m pip install -e .
```

## Check installation and version

```bash
gcon --help
gcon --version
```

## Uninstall

```bash
python3.11 -m pip uninstall gcon
```
