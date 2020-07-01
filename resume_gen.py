import os
# import sys
# sys.path.append('drive/My Drive/KoGPT2-FineTuning')

from jupyter_generator import main

ctx= 'cpu'
cachedir='~/kogpt2/'
load_path = './checkpoint/KoGPT2_checkpoint_55500.tar'


tmp_sent = input("단어 또는 문장을 입력해주세요.")
loops = int(input("몇 개의 문장을 생성하시겠습니까?"))+1
#samples = samples
sent_dict = main(temperature=1.1, tmp_sent = tmp_sent, text_size = 40, loops = loops, load_path = load_path)