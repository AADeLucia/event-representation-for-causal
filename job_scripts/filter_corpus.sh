#!/bin/bash

#$ -N filtration
#$ -j y -o $JOB_NAME-$JOB_ID.out
#$ -l ram_free=15G,mem_free=15G
#$ -t 1

CORPUS=(/export/corpora5/LDC/LDC2012T21/data/xml/nyt_eng_*.xml.gz)
# STEP=$[${#ALL_FILES[@]} / 4 + 1]
# START_INDEX=$[(SGE_TASK_ID - 1) * STEP]
# INPUT_FILES=${ALL_FILES[@]:${START_INDEX}:$STEP}

python "${EVENT_HOME}/code/gigaword_filtration.py" \
  --input-files "/export/corpora5/LDC/LDC2012T21/data/xml/nyt_eng_200405.xml.gz" \
  --output-dir "${EVENT_HOME}/data"

# Check exit status
status=$?
if [ $status -ne 0 ]
then
    echo "Task $SGE_TASK_ID failed"
    exit 1
fi

# Nothing else to do
exit 0

# Use the last task to combine the individual files and fill the missing data
if [ $SGE_TASK_ID -eq $SGE_TASK_LAST ]
then
    # Ensure that last task ID is the last task to finish
    while [ $(qstat -u $USER | grep $JOB_ID | wc -l) -ne 1 ]
    do
        # Wait patiently
        sleep 20
    done

    # Now complete wrap-up tasks

    echo "Done"
fi
