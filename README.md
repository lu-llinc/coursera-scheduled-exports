# Coursera-scheduled-exports

This project contains a program that wraps around the [courseraresearchexports](https://github.com/coursera/courseraresearchexports) python package. The program allows the user to request data exports for one or multiple courses and download them with a single command. This is useful for those who want to automate data export downloads. It also makes it less tedious to download e.g. clickstream data since the program downloads it as soon as the job is finished.

Note that only data coordinators can currently use this program, as it requests full exports including partner-level ids and clickstream data.

## Installation

To install this program, clone the repository.

## Dependencies

This program depends on:

  * Python 2.7.x
  * pip
  * courseraresearchexports

If you do not have pip installed on your platform, follow the installation instructions [here](https://pip.pypa.io/en/latest/installing.html#install-or-upgrade-pip). Alternatively, you can install [Anaconda](https://www.continuum.io/downloads).

To install dependencies, navigate to the clone repository in a terminal and run the following:

```shell
pip install -r requirements.txt
```

Please refer to the [courseraresearchexports](https://github.com/coursera/courseraresearchexports) if you encounter any issues installing the `courseraresearchexports` package.

## Usage

The program contains three required arguments and five optional arguments.

### Required arguments

  - **export_type**: either one of 'clickstream' or 'tables' depending on the data you want to download.
  - **course_slugs**: either a string of course slugs separated by a comma or the location of a `.txt` file containing course slugs. Each course slug should be placed on a new line.
  - **location**: Location where data exports will be stored. The program automatically creates two subfolders; one for the export type (e.g. 'clickstream') and one for the course slug.

### Optional arguments

  - **--clickstream_days**: When downloading clickstream data, the default is that the program downloads the last 7 days of data. This argument lets you change the number of days to any number higher than or equal to 1.
  - **--interval**: Input a specific date range over which to download clickstream data. Overrides `clickstream_days` argument. You should format the date range as YYYY-MM-DD.
  - **--save_metadata**: Save request metadata? If true, will be saved in the 'location' directory.
  - **--verbose**: Print verbose messages to the terminal? Useful if you're running the program manually.
  - **--log**: Store a log file containing detailed information? Mostly useful for debugging purposes.

### Running the program

Running the program is as simple as executing:

```shell
python call.py 'tables' 'human-language' '/users/jasper/tmp' --verbose
```

You can also query multiple course slugs in one command:

```shell
python call.py 'tables' 'terrorism, human-language' '/users/jasper/tmp' --verbose
```

Or, if you have a `.txt` file containg course slugs:

```shell
python call.py 'tables' '/users/jasper/desktop/courses.txt' '/users/jasper/tmp' --verbose
```

You can set a specific interval for clickstream data:

```shell
python call.py 'clickstream' '/users/jasper/desktop/courses.txt' '/users/jasper/tmp' --interval '2016-09-26' '2016-10-05' --verbose
```

Or you can override the default (download the past 7 days) with any number larger than or equal to 1:

```shell
python call.py 'clickstream' '/users/jasper/desktop/courses.txt' '/users/jasper/tmp' --clickstream_days 14 --verbose
```

This is useful if you use a program to schedule downloads, say, every 2 weeks instead of every 7 days.

### Argument description and help

Execute

```shell
python call.py -h
```

To get an overview and a description of the arguments.

## Other information

### Scheduling downloads

You can use e.g. crontab (linux, [example](https://github.com/JasperHG90/coursera-scheduled-exports/blob/master/extra/crontab.txt)) or automator (mac, [example](http://apple.stackexchange.com/questions/59532/create-automator-service-with-a-python-script)) to automate requests every week, month etc.

### Running the program in a VM or VPS

I use this program on a VPS. If you plan to use this program in a Virtual Machine (VM) or Virtual Private Server (VPS), you can use the [bootstrap](https://github.com/JasperHG90/coursera-scheduled-exports/blob/master/extra/bootstrap.sh) file to install all dependencies in one go.

Because Coursera uses OAuth2 and requires you to authenticate using a browser, you need to do the following: authenticate your account using your own computer. Then, look for the hidden `.coursera` folder in your home directory (e.g. `/home/<user>/.coursera/` for linux) and copy the `.pickle` file to the same folder on your VM/VPS (e.g. `/home/<vps-user-name>/.coursera`). You can now request exports on your VM/VPS.

### Requests

If you have a request (like adding a new argument), please leave it [here](https://github.com/JasperHG90/coursera-scheduled-exports/issues).

### Issues

Should you encounter any bugs or issues, please report them [here](https://github.com/JasperHG90/coursera-scheduled-exports/issues).
