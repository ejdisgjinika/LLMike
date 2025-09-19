#!/bin/bash
cd source 
configs=$(ls ../configs/*.yml)
echo $configs

for c in $configs
do
    python wheel_of_fortune.py --config_file $c
done

