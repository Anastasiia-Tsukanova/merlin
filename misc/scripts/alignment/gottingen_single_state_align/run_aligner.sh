#!/bin/bash -e

if test "$#" -ne 1; then
    echo "Usage: ./run_aligner.sh config.cfg"
    exit 1
fi

if [ ! -f $1 ]; then
    echo "Config file doesn't exist"
    exit 1
else
    source $1
fi

#############################################################
##### Create training labels for merlin with HTK tools ######
#############################################################

### Step 1: normalize lab for merlin with options: state_align or phone_align ###
### 
echo "normalizing label files for merlin..."
python ${frontend}/utils/treat_e-lite_labels.py \
                            ${WorkDir}/labels_elite \
                            ${WorkDir}/../dump/labels_elite_converted \
python ${frontend}/utils/normalize_lab_for_merlin.py \
                            ${WorkDir}/../dump/labels_elite_converted \
                            ${WorkDir}/label_no_align \
                            phone_align \
                            ${WorkDir}/file_id_list.scp 0


### tools required

if [[ ! -d "${HTKDIR}" ]]; then
    echo "Please configure path to HTK tools in config.cfg."
    exit 1
fi

### Step 2: do forced alignment using HVite 
echo "Step 2: forced alignment using HTK tools..."

sed -i s#'HTKDIR =.*'#'HTKDIR = "'$HTKDIR'"'# forced_alignment.py
sed -i s#'work_dir =.*'#'work_dir = "'$WorkDir'"'# forced_alignment.py
sed -i s#'multiple_speaker =.*'#'multiple_speaker = "'$multispeaker'"'# forced_alignment.py
sed -i s#'wav_dir =.*'#'wav_dir = "'$wavdata'"'# forced_alignment.py

python forced_alignment.py

echo "Your labels should be ready in label_state_align."

