#!/bin/bash

if test "$#" -lt 3; then
    echo "Usage: ./scripts/prepare_labels_from_txt.sh <path_to_text_dir> <path_to_lab_dir> <path_to_global_conf_file>"
    exit 1
fi

### arguments
inp_txt=$1
lab_dir=$2
global_config_file=$3

if [ ! -f $global_config_file ]; then
    echo "Global config file doesn't exist"
    exit 1
else
    source $global_config_file
fi

if test "$#" -eq 3; then
    train=false
    perlmode=run
    perlext=.txt
    perlinputtype=texts
    needtogeneratelabels="true"
else
    train=$4
    perlmode=train
    perlext=.txt
    perlinputtype=texts
    needtogeneratelabels="true"
fi


### tools required
if [ ! -d "${FESTDIR}" ]; then
    echo "Please configure festival path in $global_config_file !!"
    exit 1
fi

### define few variables here
frontend=${MerlinDir}/misc/scripts/frontend
out_dir=$lab_dir

if [ "$train" = true ]; then
    file_id_scp=file_id_list.scp
    scheme_file=train_sentences.scm
else
    file_id_scp=test_id_list.scp
###     scheme_file=new_test_sentences.scm
fi

if [ "$needtogeneratelabels" = true ]; then
	### Generate the labels with eLiteHTS
	echo "Generating phonetic alignment with eLiteHTS..."
	while IFS= read -r textfile
		do
			echo "Running perl ${ESTDIR}/eLiteHTS/eLiteHTS_client_mod.pl \
						${inp_txt}/${textfile}${perlext} \
						${perlinputtype} hts $perlmode \
						${lab_dir}/eLite-temp-lab/${textfile}.lab..."
			mkdir -p ${lab_dir}/eLite-temp-lab
			perl ${ESTDIR}/eLiteHTS/eLiteHTS_client_mod.pl \
						${inp_txt}/${textfile}${perlext} \
						${perlinputtype} hts $perlmode \
						${lab_dir}/eLite-temp-lab/${textfile}.lab
		done < ${out_dir}/$file_id_scp

	### Treat eLiteHTS labels for merlin
	echo "Transforming eLiteHTS labels for usage in merlin..."
	python ${frontend}/utils/treat_e-lite_labels.py \
					${lab_dir}/eLite-temp-lab \
					${lab_dir}/eLite-lab
fi

### normalize lab for merlin with options: state_align or phone_align
echo "Normalizing the label files..."
if [ "$train" = true ]; then
    python ${frontend}/utils/normalize_lab_for_merlin.py \
                            ${out_dir}/eLite-lab \
                            ${out_dir}/label_no_align \
                            phone_align \
                            ${out_dir}/$file_id_scp 0
    ### remove any un-necessary files
    rm -rf ${out_dir}/{eLite-temp-lab,eLite-lab}
else
	python ${frontend}/utils/normalize_lab_for_merlin.py \
		                    ${lab_dir}/eLite-lab \
		                    ${lab_dir}/prompt-lab \
		                    phone_align \
		                    ${out_dir}/$file_id_scp 0
	### remove any un-necessary files
	rm -rf ${lab_dir}/{eLite-temp-lab,eLite-lab}
   echo "Labels should be ready in: ${out_dir}/prompt-lab."
fi


