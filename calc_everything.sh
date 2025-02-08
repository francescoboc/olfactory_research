#!/bin/bash

# Run scripts in the background on different threads
python copy_wt_history.py &
PID1=$!
sleep 0.5
echo '' 

python calc_first_passage.py &
PID2=$!
sleep 0.5
echo '' 

python calc_successrate.py &
PID3=$!
sleep 0.5
echo '' 

python calc_successrate_com.py &
PID4=$!
sleep 0.5
echo '' 

python calc_successrate_com_theo.py &
PID5=$!
sleep 0.5
echo '' 

python calc_probability.py &
PID6=$!
sleep 0.5
echo '' 

# Wait for all background processes to complete
wait $PID1 $PID2 $PID3 $PID4 $PID5 $PID6

# Run the final Python script after all others are finished
echo 'Building lists...'
python build_lists_allbetas.py
