#!/bin/bash
cd /root
nohup jupyterhub -f config.py &> jupyterlog &
