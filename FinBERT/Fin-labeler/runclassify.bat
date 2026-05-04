@echo off
set CUDA_VISIBLE_DEVICES=0
python finetune_sentiment_classification.py --model_name "valuesimplex-ai-lab/FinBERT2-base"
