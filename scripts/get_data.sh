#!/bin/bash
scp alan@akstats.com:/home/alan/an-api/lora-data/lora.txt lora.json
grep A84041552182436A lora.json > lt22222.json
