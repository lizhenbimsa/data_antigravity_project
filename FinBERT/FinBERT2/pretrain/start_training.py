import sys
import os
import run_mlm

base_dir = os.path.dirname(os.path.abspath(__file__))

sys.argv = [
    'run_mlm.py',
    '--output_dir', os.path.join(base_dir, 'output_model'),
    '--model_name_or_path', 'valuesimplex-ai-lab/FinBERT2-base',
    '--train_data', os.path.join(base_dir, 'sample_data.jsonl'),
    '--learning_rate', '60e-5',
    '--num_train_epochs', '1',
    '--per_device_train_batch_size', '1',
    '--per_device_eval_batch_size', '1',
    '--dataloader_num_workers', '1',
    '--bf16',
    '--logging_steps', '10',
    '--save_total_limit', '50',
    '--save_steps', '10000',
    '--do_train',
    '--max_seq_length', '512',
    '--encoder_mlm_probability', '0.15',
    '--warmup_steps', '1000',
    '--weight_decay', '0.01',
    '--gradient_accumulation_steps', '1',
    '--adam_epsilon', '1e-06',
    '--adam_beta2', '0.98'
]

if __name__ == '__main__':
    run_mlm.main()
