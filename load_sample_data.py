#!/usr/bin/env python3
"""
Quick Sample Data Loader
========================

Load a smaller sample of your CSV data for testing and training.
This avoids overwhelming the system with 50,000 records at once.
"""

import pandas as pd
import json
import random
from datetime import datetime

def create_sample_dataset(csv_file, sample_size=1000, output_file='sample_dataset.json'):
    """Create a sample dataset from your CSV"""
    
    print(f"📊 Loading {csv_file}...")
    
    # Load the CSV
    df = pd.read_csv(csv_file)
    print(f"✅ Found {len(df)} total records")
    
    # Take a random sample
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"📝 Selected {sample_size} random samples")
    else:
        df_sample = df
        print(f"📝 Using all {len(df)} records")
    
    # Convert to our format
    training_data = []
    for idx, row in df_sample.iterrows():
        record = {
            'id': f'sample_{idx}',
            'symptoms_english': [row['Symptoms/Question']],
            'symptoms': row['Symptoms/Question'],
            'primary_diagnosis': row['Disease Prediction'].lower().replace(' ', '_'),
            'diagnosis': row['Disease Prediction'],
            'severity': 'medium',  # Default severity
            'confidence_score': 0.85,
            'is_emergency': False,
            'created_at': datetime.now().isoformat(),
            'data_source': 'csv_sample'
        }
        training_data.append(record)
    
    # Create dataset structure
    dataset = {
        'metadata': {
            'source_file': csv_file,
            'created_at': datetime.now().isoformat(),
            'total_samples': len(training_data),
            'sample_from': len(df),
            'data_source': 'csv_sample'
        },
        'training_data': training_data
    }
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created sample dataset: {output_file}")
    print(f"📊 Contains {len(training_data)} symptom-diagnosis pairs")
    
    return output_file

if __name__ == '__main__':
    # Create a manageable sample from your large CSV
    sample_file = create_sample_dataset(
        'medical_question_answer_dataset_50000.csv',
        sample_size=1000,
        output_file='sample_medical_dataset.json'
    )
    
    print(f"\n🚀 Next steps:")
    print(f"1. Load the sample: python manage.py load_enhanced_dataset --dataset-file {sample_file}")
    print(f"2. Train model: python manage.py train_symptom_model --force-retrain --min-samples 50")
    print(f"3. Evaluate: python manage.py evaluate_models --compare-baseline")
