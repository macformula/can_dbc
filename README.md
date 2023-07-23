# CAN Message Generator

The CAN Message Generator is a Python script designed to generate C source and header files for Controller Area Network (CAN) messages based on the Database (DBC) files. It simplifies the process of creating C files for CAN messages by automating the generation process and providing a customizable template mechanism.

## Features

- Loads CAN message definitions from DBC files.
- Automatically generates C source and header files for CAN messages.
- Provides a customizable template system for generating the files.
- Supports scaling, signed and unsigned signals, and floating-point data types.

## Installation

1. Make sure you have Python 3 installed on your system.

2. Install the required dependencies using `pip`:

`pip install cantools mako click`


3. Download or clone the repository containing the script files.

## Usage

To use the CAN Message Generator, follow these steps:

1. Prepare the JSON configuration file (ex. `configs/example.json`) with your desired settings. (use an existing or make your own .json file in that folder)

2. Run the script with the JSON configuration file as the argument:

`python canal_parser.py configs/example.json`


3. The script will read the configuration from the JSON file, process the DBC files, and generate the C source and header files based on the specified templates.

## Configuration

The configuration file (ex. `configs/tms.json`) allows you to customize various aspects of the generation process, such as:

- Paths to DBC files and output directories.
- Template locations for C source and header files.
- Ignored DBC files.
- Enabling or disabling file migration.

Please refer to the provided sample `tms.json` file for an example of the configuration settings.

## Templates

The CAN Message Generator uses the Mako template engine to generate the C source and header files. You can customize the templates to match your specific project requirements. The templates are located in the specified template directories (`TEMPLATE_LOCATION`) in the configuration file.

## Help

To view the help message and command-line options:

`python canal_parser.py --help`
