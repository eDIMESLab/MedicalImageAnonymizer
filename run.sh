#!/bin/bash

check=$(python -m pip list | grep MedicalImageAnonymizer)

if [ "$check" == "" ]; then # not yet installed

  python -m pip install -r ./requirements.txt
  python ./setup.py develop --user > /dev/null

fi

# Run the GUI

python ./MedicalImageAnonymizer/GUI/gui.py

