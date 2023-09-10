# INSTALLATION ⚙️

[◀️ Home](https://github.com/sgelias/gene-connector-cli/blob/main/README.md) | [◀️ Documentation](https://github.com/sgelias/gene-connector-cli/blob/main/docs/README.md)

___

The installation procedure is the same for all platforms. The main requirement
is Python 3.11. The recommended way to install is using `pip`:

## Install from PyPI

```bash
pip install gene-connector-cli
```

If you already have a previous version installed, you can upgrade using:

```bash
pip install --upgrade --force-reinstall gene-connector-cli
```

## Install from source

```bash
git clone https://github.com/sgelias/gene-connector-cli.git
cd gene-connector-cli
pip install .
```

## Install from source (editable)

```bash
pip install -e .
```

## Check installation and version

Gene Connector CLI is a command line interface (CLI) tool, them main command being `gcon`, available after installation. See [usage guide](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/02_usage.md) for details.

```bash
gcon --help
gcon --version
```

## Uninstall

```bash
pip uninstall gene-connector-cli
```

___

⚠️ **IMPORTANT**: If your environment contains more than one python version installed, you include `python3.11 -m` before `pip` in the above commands. Example:

```bash
python3.11 -m pip install gene-connector-cli
```

___

[▶️ Next: Usage](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/02_usage.md)
