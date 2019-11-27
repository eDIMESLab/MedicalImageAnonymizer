| **Author**   | **Project** | **Documentation**                                                                   | **Build Status**              |
|:------------:|:-----------:|:-----------------------------------------------------------------------------------:|:-----------------------------:|
|   [**N. Curti**](https://github.com/Nico-Curti) <br/> [**E. Giampieri**](https://github.com/EnricoGiampieri)   |  **MedicalImageAnonymizer**  | [![docs](https://img.shields.io/badge/documentation-latest-blue.svg?style=plastic)](https://github.com/eDIMESLab/MedicalImageAnonymizer/blob/master/docs/usage.png) | **Linux/MacOS** : [![travis](https://travis-ci.com/eDIMESLab/MedicalImageAnonymizer.svg?branch=master)](https://travis-ci.com/eDIMESLab/MedicalImageAnonymizer) <br/> **Windows** : [![appveyor](https://ci.appveyor.com/api/projects/status/wmf0gd3txx88d6p6?svg=true)](https://ci.appveyor.com/project/Nico-Curti/medicalimageanonymizer) |

[![GitHub pull-requests](https://img.shields.io/github/issues-pr/eDIMESLab/MedicalImageAnonymizer.svg?style=plastic)](https://github.com/eDIMESLab/MedicalImageAnonymizer/pulls)
[![GitHub issues](https://img.shields.io/github/issues/eDIMESLab/MedicalImageAnonymizer.svg?style=plastic)](https://github.com/eDIMESLab/MedicalImageAnonymizer/issues)

[![GitHub stars](https://img.shields.io/github/stars/eDIMESLab/MedicalImageAnonymizer.svg?label=Stars&style=social)](https://github.com/eDIMESLab/MedicalImageAnonymizer/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/eDIMESLab/MedicalImageAnonymizer.svg?label=Watch&style=social)](https://github.com/eDIMESLab/MedicalImageAnonymizer/watchers)

<a href="https://github.com/eDIMESLab">
<div class="image">
<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="90" height="90">
</div>
</a>

# Medical Image Anonymizer - MIA

Different kind of anonymizers for the most common bio-medical image formats.

|  **Image fmt**  |     **Windows**             |    **Linux/MacOS**          |
|:---------------:|:---------------------------:|:---------------------------:|
| .SVS (or .Tiff) | :+1:                        | :+1:                        |
|     .dcm        | :+1:                        | :+1:                        |
|     .nii        | :+1:                        | :+1:                        |

1. [Installation](#installation)
2. [Authors](#authors)
3. [License](#license)
4. [Contributions](#contributions)
5. [Acknowledgments](#acknowledgments)
6. [Citation](#citation)


## Installation

First of all ensure that a right Python version is installed (Python >= 3.4 is required). <!-- to check -->
The [Anaconda/Miniconda](https://www.anaconda.com/) python version is recommended.

Download the project or the latest release:

```bash
git clone https://github.com/eDIMESLab/MedicalImageAnonymizer
cd MedicalImageAnonymizer
```

To install the prerequisites type:

```bash
pip install -r ./requirements.txt
```

In the `MedicalImageAnonymizer` directory execute:

```bash
python setup.py install
```

or for installing in development mode:

```bash
python setup.py develop --user
```

## Usage

The simplest usage of this package is given by its GUI version.
You can simply run the [gui.py](https://github.com/eDIMESLab/MedicalImageAnonymizer/blob/master/MedicalImageAnonymizer/GUI/gui.py) script and obtain a very simple interface to manage the file anonymisation.

```bash
python ./MedicalImageAnonymizer/GUI/gui.py
```

or inside Python

```python
import MedicalImageAnonymizer as mia

mia.GUI()
```

![Medical Image Anonymizer Graphic Interface](https://github.com/eDIMESLab/MedicalImageAnonymizer/blob/master/docs/usage.png)

If you want a more deep usage of this package you can import the different modules into your Python code.
Lets take as example the SVS anonymisation.

First of all import the appropriated module

```python
import MedicalImageAnonymizer as mia

# Create the Anonymizer object
svsfile = 'test.svs'
anonym = mia.SVSAnonymize(svsfile)

# Anonymize the input file
anonym.anonymize(infolog=True)

# Invert the anonymization using the informations stored in the informations log created
anonym.deanonymize(infolog=True)
```

Now you can notice that two additional files are created by this script: `test_anonym.svs` and `test_info.json`.
The `test_anonym.svs` is the anonymized version of the input file (`test.svs`).
All the informations related to the patients are nuked in the anonymized file version and they are stored into the information log file (`test_info.json`).
In this way you can simply revert the anonymization using the `deanonymize` member function which re-apply the sensitive informations to the original file.

To check this condition you can run

```bash
diff test.svs test_anonym.svs
```

and (if you had manually copied the input file before the anonymization into `test_original.svs`)

```bash
diff test_original.svs test.svs
```

This can be useful if you want to share and process the images stored into the original file keeping safe the sensitive informations and only at the end resume these informations.

**DANGER ZONE** - However, you can turned off the information storage using `infolog=False`: in this way the original file will be overwritten by its anonymous version.

The same syntax could be used for the different file formats.

## Authors

* **Enrico Giampieri** [git](https://github.com/EnricoGiampieri), [unibo](https://www.unibo.it/sitoweb/enrico.giampieri)
* **Nico Curti** [git](https://github.com/Nico-Curti), [unibo](https://www.unibo.it/sitoweb/nico.curti2)

See also the list of [contributors](https://github.com/eDIMESLab/MedicalImageAnonymizer/contributors) [![GitHub contributors](https://img.shields.io/github/contributors/eDIMESLab/MedicalImageAnonymizer.svg?style=plastic)](https://github.com/eDIMESLab/MedicalImageAnonymizer/graphs/contributors/) who participated in this project.

## License

The `MedicalImageAnonymizer` package is licensed under the MIT "Expat" License. [![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/eDIMESLab/MedicalImageAnonymizer/blob/master/LICENSE.md)


### Contributions

Any contribution is more than welcome. Just fill an issue or a pull request and I will check ASAP!

If you want update the list of layer objects please pay attention to the syntax of the layer class and to the names of member functions/variables used to prevent the compatibility with other layers and utility functions.


### Acknowledgments

Thanks goes to all contributors of this project.

### Citation

Please cite `MedicalImageAnonymizer` if you use it in your research.

```tex
@misc{MedicalImageAnonymizer,
  author = {Enrico Giampieri and Nico Curti},
  title = {Medical Image Anonymizer},
  year = {2019},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/eDIMESLab/MedicalImageAnonymizer}},
}
```

