import sys
import os

# Change to the correct directory
os.chdir(r'C:\Users\Administrator\.openclaw\workspace\1b_training_data')

# Import and run the trainer
from erbing_continuous_trainer import ErbingContinuousTrainer

if __name__ == '__main__':
    trainer = ErbingContinuousTrainer()
    trainer.run_continuous(save_interval=10, max_steps=100)
