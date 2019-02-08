#!/bin/bash

./generate_config.py
rm -rf /opt/unetlab/tmp/0/38d9df61-a249-4988-bd4b-4fe5080b2865
cp lab.unl /opt/unetlab/labs/BGP-backbone-generated.unl
chown www-data /opt/unetlab/labs/BGP-backbone-generated.unl
