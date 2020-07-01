import os
import torch
from gluonnlp.data import SentencepieceTokenizer
from kogpt2.model.sample import sample_sequence
from kogpt2.utils import get_tokenizer
from kogpt2.utils import download, tokenizer
from kogpt2.model.torch_gpt2 import GPT2Config, GPT2LMHeadModel
import gluonnlp

def auto_enter(text):
	text = (text.replace("   ", "\n"))
	text = text.split("\n")

	text = [t.lstrip() for t in text if t != '']
	return "\n\n".join(text)

def main(temperature = 0.7, top_p = 0.8, top_k = 40, tmp_sent = "", text_size = 100, loops = -1,
	load_path = 'load_path_of_your_model', ctx= 'cpu',cachedir='~/kogpt2/', samples="path to save samples"):

	pytorch_kogpt2 = {
		'url': 'https://kobert.blob.core.windows.net/models/kogpt2/pytorch/pytorch_kogpt2_676e9bcfa7.params',
		'fname': 'pytorch_kogpt2_676e9bcfa7.params',
		'chksum': '676e9bcfa7'
	}

	kogpt2_config = {
		"initializer_range": 0.02,
		"layer_norm_epsilon": 1e-05,
		"n_ctx": 1024,
		"n_embd": 768,
		"n_head": 12,
		"n_layer": 12,
		"n_positions": 1024,
		"vocab_size": 50000
	}

	model_info = pytorch_kogpt2
	model_path = download(model_info['url'],
						  model_info['fname'],
						  model_info['chksum'],
						  cachedir=cachedir)

	vocab_info = tokenizer
	vocab_path = download(vocab_info['url'],
						  vocab_info['fname'],
						  vocab_info['chksum'],
						  cachedir=cachedir)

	device = torch.device(ctx)

	# 저장한 Checkpoint 불러오기
	checkpoint = torch.load(load_path, map_location=device)

	# KoGPT-2 언어 모델 학습을 위한 GPT2LMHeadModel 선언
	kogpt2model = GPT2LMHeadModel(config=GPT2Config.from_dict(kogpt2_config))
	kogpt2model.load_state_dict(checkpoint['model_state_dict'])

	kogpt2model.eval()
	vocab_b_obj = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
															  mask_token=None,
															  sep_token=None,
															  cls_token=None,
															  unknown_token='<unk>',
															  padding_token='<pad>',
															  bos_token='<s>',
															  eos_token='</s>')

	tok_path = get_tokenizer()

	model, vocab = kogpt2model, vocab_b_obj
	vocab.token_to_idx["\n"] = vocab.token_to_idx["<unused0>"]
	del vocab.token_to_idx["<unused0>"]

	tok = SentencepieceTokenizer(tok_path)
	num = 0

	"""
	자소서가 저장될 수 있는 딕셔너리(테이블) 생성 후
	자소서가 생성될 때마다 추가될 수 있도록 함
	입력한 개수만큼 자소서가 생성된 후에는 딕셔너리를 반환
	"""
	sent_dict = {}

	if loops != -1:
		num = 1

	while 1:
		sent =''
		if tmp_sent == "":
			tmp_sent = input('input : ')
		sent = sent+tmp_sent

		toked = tok(sent)

		if len(toked) > 1022:
			break

		sent = sample_sequence(model, tok, vocab, sent, text_size, temperature, top_p, top_k)
		sent = sent.replace("<unused0>", "\n") # 비효율적이지만 엔터를 위해서 등장
		sent = auto_enter(sent)
		
		sent_dict[num] = sent

		if num:
			num += 1
			if num >= loops:
				print("good")
				return sent_dict