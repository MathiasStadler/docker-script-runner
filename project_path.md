# project _path
<!-- keep the format ktf -->
## init folder
<!-- ktf -->
```bash <!-- markdownlint-disable-line code-block-style -->
 mkdir docker-script-runner && cd $_

 touch project_path.md
```
<!-- KtF-->
## detect os version
<!-- KtF-->
```bash
cat /etc/debian_version
Debian 13.7 
```
<!-- ktf -->
## detect python version
<!-- ktf -->
```bash <!-- markdownlint-disable-line code-block-style -->
python3 --version
Python 3.13.5
```
<!-- KtF-->
## create venv

[install venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)

```bash <!-- markdownlint-disable-line code-block-style -->
python3 -m venv .venv
```
<!-- ktf -->
## enter .venv

```bash <!-- markdownlint-disable-line code-block-style -->
source .venv/bin/activate
```
<!-- ktf -->
## list installed packages

```bash <!-- markdownlint-disable-line code-block-style -->
pip list
```
<!-- ktf -->
## install packages - example
<!-- ktf -->
```bash <!-- markdownlint-disable-line code-block-style -->
pip install requests
pip install urllib3
```
<!-- ktf -->
## exit/leave .venv
<!-- ktf -->
```bash
deactivate
```
<!-- ktf -->
## Automatically create file 'requirements.txt' from running project [![alt text][1]](https://stackoverflow.com/questions/31684375/automatically-create-file-requirements-txt)
<!-- ktf -->
```bash
pip install pipreqs
pipreqs /path/to/project
```
<!-- ktf -->
<!-- To comply with the format -->
<!-- Link sign - Don't Found a better way :-( - You know a better method? - send me a email -->
>[!NOTE]
>Symbol to mark web external links [![alt text][1]](./README.md)
<!-- spell-checker: disable  -->
<!-- keep the format -->
<!-- make folder and download the link sign vai curl -->
<!-- mkdir -p img && curl --create-dirs --output-dir img -O  "https://raw.githubusercontent.com/MathiasStadler/link_symbol_svg/refs/heads/main/link_symbol.svg"-->
<!-- Link sign - Don't Found a better way :-( - You know a better method? - **send me a email** -->
[1]: ./img/link_symbol.svg
<!-- keep the format -->