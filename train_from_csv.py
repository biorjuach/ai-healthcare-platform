#!/usr/bin/env python3
"""
Direct CSV Training Script
========================

Train your ML model directly from your CSV file without going through Django.
This is faster and avoids database complications.
"""

import pandas as pd
import pickle
import json
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import numpy as np

def train_model_from_csv(csv_file, model_output='models/symptom_classifier.pkl', 
                        metadata_output='models/symptom_classifier_metadata.json'):
    """Train ML model directly from CSV file"""
    
    print(f"🚀 Training ML model from {csv_file}")
    
    # Load CSV data
    print("📊 Loading CSV data...")
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} records")
    
    # Prepare training data
    print("🔄 Preparing training data...")
    
    # Use symptoms as features (X) and diagnoses as labels (y)
    X = df['Symptoms/Question'].fillna('').astype(str)
    y = df['Disease Prediction'].fillna('general_consultation').astype(str)
    
    # Clean and normalize diagnosis names
    y = y.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    print(f"📈 Training data prepared:")
    print(f"   Symptoms (X): {len(X)} samples")
    print(f"   Diagnoses (y): {len(y.unique())} unique conditions")
    print(f"   Top conditions: {y.value_counts().head().to_dict()}")
    
    # Split data
    print("🔀 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # Create ML pipeline
    print("🤖 Creating ML pipeline...")
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=1500,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2,
            max_df=0.9
        )),
        ('classifier', RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    # Train the model
    print("🎯 Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate the model
    print("📊 Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Model trained successfully!")
    print(f"   Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Cross-validation
    print("🔄 Running cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"   CV Score: {cv_scores.mean():.3f} ± {cv_scores.std()*2:.3f}")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the model
    print(f"💾 Saving model to {model_output}...")
    with open(model_output, 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'source_file': csv_file,
        'accuracy': accuracy,
        'cv_score_mean': cv_scores.mean(),
        'cv_score_std': cv_scores.std(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'total_samples': len(X),
        'classes': sorted(y.unique()),
        'top_conditions': y.value_counts().head(10).to_dict(),
        'feature_count': model.named_steps['tfidf'].get_feature_names_out().shape[0] if hasattr(model.named_steps['tfidf'], 'get_feature_names_out') else 1500
    }
    
    with open(metadata_output, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 Metadata saved to {metadata_output}")
    
    # Print detailed results
    print(f"\n📈 Training Results:")
    print(f"   Source: {csv_file}")
    print(f"   Total samples: {len(X):,}")
    print(f"   Unique conditions: {len(y.unique())}")
    print(f"   Model accuracy: {accuracy:.1%}")
    print(f"   Cross-validation: {cv_scores.mean():.1%} ± {cv_scores.std()*2:.1%}")
    print(f"   Model saved: {model_output}")
    
    # Show classification report for top classes
    print(f"\n📊 Classification Report (top conditions):")
    # Get top 10 most common classes for the report
    top_classes = y.value_counts().head(10).index.tolist()
    y_test_filtered = y_test[y_test.isin(top_classes)]
    y_pred_filtered = y_pred[y_test.isin(top_classes)]
    
    if len(y_test_filtered) > 0:
        print(classification_report(y_test_filtered, y_pred_filtered, 
                                  labels=top_classes, target_names=top_classes))
    
    return model, metadata

def test_model_predictions(model_file='models/symptom_classifier.pkl'):
    """Test the trained model with sample predictions"""
    
    print(f"\n🧪 Testing model predictions...")
    
    try:
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
    except:
        print(f"❌ Could not load model from {model_file}")
        return
    
    # Test samples
    test_samples = [
        "fever and headache",
        "chest pain and difficulty breathing", 
        "persistent cough and fatigue",
        "nausea and vomiting",
        "back pain and stiffness"
    ]
    
    print("Sample predictions:")
    for sample in test_samples:
        try:
            prediction = model.predict([sample])[0]
            confidence = max(model.predict_proba([sample])[0])
            print(f"   '{sample}' → {prediction} (confidence: {confidence:.1%})")
        except Exception as e:
            print(f"   Error predicting '{sample}': {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train ML model directly from CSV')
    parser.add_argument('--csv-file', default='medical_question_answer_dataset_50000.csv', 
                       help='Path to CSV file')
    parser.add_argument('--sample-size', type=int, help='Use only a sample of the data')
    parser.add_argument('--test-predictions', action='store_true', 
                       help='Test the model with sample predictions after training')
    
    args = parser.parse_args()
    
    # Load and optionally sample the data
    if args.sample_size:
        print(f"📝 Using sample of {args.sample_size} records...")
        df = pd.read_csv(args.csv_file)
        df_sample = df.sample(n=min(args.sample_size, len(df)), random_state=42)
        sample_file = f'sample_{args.sample_size}_medical_data.csv'
        df_sample.to_csv(sample_file, index=False)
        csv_file = sample_file
    else:
        csv_file = args.csv_file
    
    # Train the model
    model, metadata = train_model_from_csv(csv_file)
    
    # Test predictions if requested
    if args.test_predictions:
        test_model_predictions()
    
    print(f"\n🎉 Training complete! Your model is ready to use.")
    print(f"\n🚀 Next steps:")
    print(f"1. Test your model: python train_from_csv.py --test-predictions")
    print(f"2. Use in your app: The model file is at models/symptom_classifier.pkl")
    print(f"3. Check the web interface to see improved predictions!")
