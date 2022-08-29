# About d7&#46;py ( Decompress with 7-Zip )
This tool decompresses compressed files using 7-Zip.
**You need a 7-Zip executable and library to use this script.**  
When I unzip a McAfee quarantine item, the path is garbled. To avoid this problem, I created a script that can specify a code page.
&nbsp;  
## Features 
The main features are as follows:
- You can specify the code page identifier. Used when the path of the decompressed ZIP file is garbled. (-c option)  
This option affects TAR and ZIP formats. Default encoding for TAR and ZIP formats may be different. Therefore, you should not extract TAR and ZIP formats together if you use this option.
- The specified file and all files contained in the specified directory will be decompressed with 7zip. Files are not selected by extension. (-i option)
- You can specify the output directory. If not specified, it will be expanded in the same location as the compressed file. (-o option)
- You can specify the password to decrypt the encrypted compressed files. (-p option)
&nbsp;  
&nbsp;  
## Installation and Configuration
### 1.&nbsp;&nbsp;Check Python version ( version >= 3.6 required )
Available since Python 3.6.
To check the version, at the command prompt or terminal type:
```
python -V
```
or
```
python
```
Upgrade Python to the latest version if nessasary.  
[https://www.python.org/downloads/](https://www.python.org/downloads/)
&nbsp;  
### 2.&nbsp;&nbsp;Clone this repository
Change the current directory to the location where you want to install and run the following command:
```
git clone https://github.com/1kmt/decompress7z.git
cd decompress7z
```
### 3.&nbsp;&nbsp;Need 7-Zip executable for working
In the default configuration, the script and 7-Zip executable must be stored in the same directory.
```python
DEFAULT_7ZIP_PATH = "./7z.exe"
```
When stored in the same directory, it looks like this:
```
C:\tools\d7>dir

2019/02/22  01:00         1,679,360 7z.dll
2019/02/22  01:00           468,992 7z.exe
2022/07/23  10:22             6,953 d7.py
```
If you want to change the location of the 7-Zip executable, there are two ways.
- Modify the default settings in the source code.
```python
DEFAULT_7ZIP_PATH = "C:/Program Files/7-Zip/7z.exe"
```
- Specify the 7-Zip executable path using the -x option.
```
python d7.py -i ./filename.zip -x "C:/Program Files/7-Zip/7z.exe"
```
### 4.&nbsp;&nbsp;Run
See 'Command line examples'
&nbsp;  
&nbsp;  
## Usage
```
usage: d7.py [-h] [-c CODEPAGE] -i INPUT [-o OUTPUT] [-p PASSWORD] [-v]
             [-x EXE]

The specified file and all files contained in the specified directory
(recursive=False) will be decompressed with 7-Zip. Files are not selected by
extension. It also requires 7-Zip executable and library to run.

optional arguments:
  -h, --help            show this help message and exit
  -c CODEPAGE, --codepage CODEPAGE
                        specify the code page identifier(utf-8:65001, shift-
                        jis:932, EUC-JP:20932, etc). used when the path of the
                        decompressed ZIP file is garbled.
  -i INPUT, --input INPUT
                        specify the compressed file or directory containing
                        compressed files.
  -o OUTPUT, --output OUTPUT
                        specify the output directory.
  -p PASSWORD, --password PASSWORD
                        specify the password to decrypt the encrypted
                        compressed files (ZIP, 7z, RAR).
  -v, --version         show program's version number and exit
  -x EXE, --exe EXE     specify the 7-Zip executable path.
```
### &#9635;&nbsp;&nbsp;Command line examples
The -i option can specify a compressed file or the directory containing the compressed files.
This option can be used multiple times.
```
python d7.py -i ./filename.zip
python d7.py -i ./filename1.zip -i ./filename2.rar -i ./dirname
```
Specify the output directory with the -o option
```
python d7.py -i ./filename.zip -o C:/Users/xxx/Desktop/outdir
```
Specify the password to decrypt the encrypted compressed file with the -p option.
```
python d7.py -i ./filename.zip -p infected
```
Use the -c option when the path of the decompressed ZIP file is garbled.
Specify the code page identifier as a 2- to 5-digit number.
```
python d7.py -i ./filename.zip -p infected -c 65001
```
|Identifier|Character encoding|
| :--- | :--- |
|932|Shift-JIS|
|20932|EUC-JP|
|65000|Unicode (UTF-7)|
|65001|Unicode (UTF-8)|
|etc|...|
