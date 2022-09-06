#!/usr/bin/bash
export PATH="$PATH:/share/bin"
export PATH="$PATH:/usr/local/bin"
export PATH="$PATH:/data/home/zhuyf/programs/anaconda3/bin"

INPUT_FILE=/data/home/zhuyf/homemade_jade_patch/jp5_test/input_auto.inp
JADEPATCH_DIR=$(grep "^jade_patch_dir" ${INPUT_FILE}|cut -d= -f2|sed 's/^[ \t]*//g')

WORK_DIR=$(grep "^all_dir" ${INPUT_FILE} | cut -d= -f2|sed 's/^[ \t]*//g')
RESULT=${WORK_DIR}auto_check_qsub.log

cd ${JADEPATCH_DIR}

echo `date +%Y-%m-%d@%H:%M:%S` >> ${RESULT}

result=$(tail -10 ${RESULT} | grep -c 'EMPTY' )

if [ $result -ne 0 ]
then
    echo "$(crontab -l)" >> ${RESULT}
    echo `crontab -r`
else
    python3 ${JADEPATCH_DIR}Auto_check.py >> ${RESULT}
    echo -e  "\n\n"  >> ${RESULT}
fi

