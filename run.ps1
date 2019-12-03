#!/usr/bin/env pwsh

$check = python.exe -m pip list | Select-String -Pattern "MedicalImageAnonymizer"

If( $null -eq $check )
{
  python.exe -m pip install -r .\requirements.txt
  python.exe .\setup.py develop --user > $null
}

python.exe .\MedicalImageAnonymizer\GUI\gui.py
