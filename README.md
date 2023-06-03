# Color Harmonization

A Python implementation of the paper **Color Harmonization** (https://dl.acm.org/doi/abs/10.1145/1179352.1141933) with GUI

## How to run

### Color Harmonization only (w/o Super Resolution)

*This has already realized all things in the original paper*

1. Use Python 3.8
1. ```git clone https://github.com/Rekkursion/ColorHarmonization_Qt.git```
1. ```cd ColorHarmonization_Qt```
1. Create and activate a virtual environment for Python 3.8 (optional, but recommended)
1. ```pip install -r requirements.txt```
1. Now one can already run the GUI by ```python main.py```, but without the feature of Super Resolution

### Color Harmonization w/ Super Resolution

*Reference: https://github.com/xinntao/Real-ESRGAN/*

7. Follow the first 5 steps listed above
1. ```git clone https://github.com/xinntao/Real-ESRGAN.git```
1. ```cd Real-ESRGAN```
1. ```pip install -r requirements.txt```
1. ```python setup.py develop```
1. ```cd ..```
1. Run the GUI by ```python main.py```, with the feature of Super Resolution activated

