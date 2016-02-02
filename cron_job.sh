#!/bin/bash
#
# Run market_report scripts for today. Constants hard-coded due to short
# length.

start_date=`/bin/date -v -56d +%Y%m%d`  # YYYYMMDD 8 weeks ago.
end_date=`/bin/date +%Y%m%d`  # YYYYMMDD today.
universe_cmd="./universe_main.py --config_file universe_config.yaml
  --output_dir universe_data/${end_date}/ --start_date ${start_date}
  --end_date ${end_date}"

eval "pkill tor.real"  # Kill any existing TOR processes.
eval "export PYTHONPATH=/Users/peter/Desktop/Code"
eval "cd /Users/peter/Desktop/Code/market_report"

counter=0
while [ $counter -lt 5 ]; do  # Max 5 retries.
  let counter=counter+1
  echo "Attempt: ${counter}"
  echo $universe_cmd
  eval $universe_cmd
  if [ $? -eq 0 ];
  then
    break
  fi
done
