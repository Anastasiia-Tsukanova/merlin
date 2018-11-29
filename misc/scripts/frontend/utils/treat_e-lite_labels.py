import sys,os
from shutil import copy2 as cpy

separators = ["^", "-", "+", "=", "@", "/"] # Watch out, there is schwa encoded as @
translate = {'a': 'a', 'l': 'l', 'O': 'oopen', 'R': 'r', '_': 'pau', 'pau': 'pau', 'e': 'e', 'z': 'z', 'v': 'v', 'a~': 'an', 't': 't', 'Z': 'zh', 'e~': 'en', 'k': 'k', 'o~': 'on', 'n': 'n', 'j': 'j', 'J': 'gn', 'd': 'd', 'b': 'b', 'i': 'i', 'p': 'p', 'm': 'm', 'E': 'eps', '@': 'schwa', 'y': 'y', 'o': 'o', 'u': 'u', 's': 's', '2': 'deux', 'S': 'sh', 'f': 'f', 'w': 'w', '9~': 'oen', 'H': 'h', 'g': 'g', '9': 'oe', 'N': 'nn', 'x': 'x'}

def parse(label, counter):
    # p1^p2- p3+p4=p5 @p6 p7/A:a1 a2 a3 /B:b1-b2-b3 @b4-b5 &b6-b7 #b8-b9 $b10-b11
    # !b12-b13 ;b14-b15 |b16 //C:c1+c2+c3/D:d1 d2 /E:e1+e2 @e3+e4 &e5+e6 #e7+e8
    # /F: f1 f2/G:g1 g2 /H:h1=h2 @h3=h4|h5 /I:i1 i2/J: j1+ j2- j3

    # 0 500000 x^x-a+l=O@1_1/A:0_0_/B:1-1-1@1-2&1-2#0-1$0-1!0-1;0-1|a/C:1+1+3/D:x_0/E:ADV+2@1+1&0+0#0+1/F:LIGHTPUNCT-1/G:0_0/H:2=1@0=6|NONE/I:1_1/J:20+12-7
    if " " in label:
        t0 = label.find(" ")
        prefix = label[:label.find(" ", t0+1)]
        no_invented_time_stamps = True
    else:
        no_invented_time_stamps = False
        prefix = "{} {}".format(100000*counter, 100000*(counter+1)) # Add false duration information
    phonemes = list()
    prev_idx = len(prefix) if no_invented_time_stamps else -1
    for sep in separators[:-2]:
        phonemes.append(label[prev_idx+1:label.find(sep)])
        prev_idx = label.find(sep)
    no_ph_beyond = label.find(separators[-1])
    phonemes.append(label[prev_idx+1:label[:no_ph_beyond].rfind(separators[-2])])
    prev_idx = label[:no_ph_beyond].rfind(separators[-2])
    rest = label[prev_idx+1:]
    return prefix, phonemes, rest

def encode(prefix, phonemes, rest):
    label = prefix + " " if prefix else ''
    for ph, sep in zip(phonemes, separators):
        label += translate[ph] + sep
    return label+rest

def make_concise(labels):
    conc_labels = list()
    same_lab_since = 0
    for curr_line, next_line in zip(labels, labels[1:]):
        
        curr_t_start, curr_t_end, curr_rest = curr_line.split(' ')
        # print(curr_t_start + ' +++ '+  curr_t_end + ' +++ '+  curr_rest)
        next_t_start, next_t_end, next_rest = next_line.split(' ')
        curr_t_start, curr_t_end, next_t_start, next_t_end = map(lambda x: int(x), [curr_t_start, curr_t_end, next_t_start, next_t_end])
        def cut(line, symb):
            cut_line = line.split(symb)
            phonemes, label = cut_line[0], symb.join(cut_line[1:])
            try:
                num = int(label[label.rfind('[')+1:label.rfind(']')])
            except:
                num = None
            return phonemes, label[:label.rfind('[')], num
        curr_phonemes, curr_label, _ = cut(curr_rest, '@')
        next_phonemes, next_label, _ = cut(next_rest, '@')
        # if '/E:ENDPUNCT+' in curr_label and '/E:ENDPUNCT+' not in next_label:
        #     midpoint = min(curr_t_start, int(0.5*(same_lab_since + curr_t_end)))
        #     conc_labels.append("{} {} {}@{}\n".format(coef*curr_t_start, coef*midpoint, curr_phonemes, curr_label))
        #     conc_labels.append("{} {} {}@{}\n".format(coef*midpoint, coef*curr_t_end, curr_phonemes, curr_label))
        #     same_lab_since = next_t_start
        if curr_phonemes != next_phonemes or curr_label != next_label:
            conc_labels.append("{} {} {}@{}\n".format(same_lab_since, curr_t_end, curr_phonemes, curr_label))
            same_lab_since = next_t_start
    conc_labels.append("{} {} {}@{}".format(same_lab_since, next_t_end, next_phonemes, next_label))
    return conc_labels

if __name__ == "__main__":

    if len(sys.argv)<2:
        print('Usage: python treat_e-lite_labels.py <e-lite_output_dir> <e-lite_labels_converted_dir>\n')
        sys.exit(0)

    elite_in_dir   = sys.argv[1]
    elite_out_dir  = sys.argv[2]

    # Treat Gottingen data:
    # wav_dir = os.path.join(elite_in_dir, '..', 'gottingen_wav')
    # scp_file = os.path.join(elite_in_dir, '..', 'file_id_list.scp')
    # def remove_underscores(directory):
    #     for dp, dn, fn in os.walk(directory):
    #         for f in fn:
    #             os.rename(os.path.join(dp, f), os.path.join(dp, f.replace("_", ""))) 
    # remove_underscores(elite_in_dir)
    # remove_underscores(wav_dir)
    # with open(scp_file, 'r') as scp_f:
    #     file_list = scp_f.read()
    # with open(scp_file, 'w') as scp_f:
    #     scp_f.write(file_list.replace("_", ""))

    speakers = [sp for sp in os.listdir(elite_in_dir) if os.path.isdir(os.path.join(elite_in_dir,sp))]
    if speakers == list():
        speakers = ['']
    for sp in speakers:
        if not os.path.exists(os.path.join(elite_out_dir,sp)):
            os.makedirs(os.path.join(elite_out_dir,sp))
        for f_raw in os.listdir(os.path.join(elite_in_dir,sp)):
            f_conv = f_raw[:-4]+'.lab'
            cpy(os.path.join(elite_in_dir,sp,f_raw), os.path.join(elite_out_dir,sp,f_conv))
            with open(os.path.join(elite_out_dir,sp,f_conv), 'r') as f_before:
                labels_in = f_before.readlines()
            with open(os.path.join(elite_out_dir,sp,f_conv), 'w') as f_after:
                labels_out = list()
                skip = False
                for counter, label in enumerate(labels_in):
                    if len(label) > 1 and not skip:
                        pref, phs, rest = parse(label, counter)
                        labels_out.append(encode(pref, phs, rest))
                    else:
                        skip = True
                        # labels_out.append(label)
                # labels_out = make_concise(labels_out)
                f_after.write("".join(labels_out))

