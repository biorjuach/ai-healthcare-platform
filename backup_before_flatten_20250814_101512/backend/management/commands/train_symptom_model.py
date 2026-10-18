from django.core.management.base import BaseCommand
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import pickle
import os
import json
import numpy as np
from datetime import datetime, timedelta
from backend.models import Symptom, Diagnosis, Patient
from backend.ai_services import SymptomAnalyzer

class Command(BaseCommand):
    help = 'Train symptom classification model using historical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-days',
            type=int,
            default=365,
            help='Number of days of historical data to use for training'
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Proportion of data to use for testing'
        )
        parser.add_argument(
            '--min-samples',
            type=int,
            default=50,
            help='Minimum number of samples required to train model'
        )
        parser.add_argument(
            '--force-retrain',
            action='store_true',
            help='Force retraining even if model exists'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting symptom model training...')
        
        # Create models directory if it doesn't exist
        models_dir = 'models'
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            self.stdout.write(f'Created models directory: {models_dir}')
        
        model_path = os.path.join(models_dir, 'symptom_classifier.pkl')
        
        # Check if model exists and force retrain flag
        if os.path.exists(model_path) and not options['force_retrain']:
            self.stdout.write('Model already exists. Use --force-retrain to retrain.')
            return
        
        # Get training data
        training_data = self._get_training_data(options['data_days'])
        
        if len(training_data) < options['min_samples']:
            self.stdout.write(
                self.style.WARNING(
                    f'Insufficient training data. Found {len(training_data)} samples, '
                    f'minimum required: {options["min_samples"]}'
                )
            )
            return
        
        # Prepare data
        X, y = self._prepare_training_data(training_data)
        
        if len(set(y)) < 2:
            self.stdout.write(
                self.style.WARNING('Insufficient class diversity for training')
            )
            return
        
        # Split data
        # Split data into training and testing sets
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=options['test_size'], random_state=42, stratify=y
            )
        except ValueError:
            # If stratification fails due to insufficient samples per class, use random split
            self.stdout.write(
                self.style.WARNING(
                    'Warning: Insufficient samples per class for stratified split. Using random split instead.'
                )
            )
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=options['test_size'], random_state=42
            )
        
        # Create and train model
        model = self._create_model()
        
        self.stdout.write('Training model...')
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.stdout.write(f'Model accuracy: {accuracy:.3f}')
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5)
        self.stdout.write(f'Cross-validation scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})')
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save model metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'accuracy': accuracy,
            'cv_score_mean': cv_scores.mean(),
            'cv_score_std': cv_scores.std(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'classes': list(set(y)),
            'feature_names': model.named_steps['tfidf'].get_feature_names_out().tolist() if hasattr(model.named_steps['tfidf'], 'get_feature_names_out') else []
        }
        
        metadata_path = os.path.join(models_dir, 'symptom_classifier_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Model trained successfully and saved to {model_path}'
            )
        )
        
        # Print classification report
        self.stdout.write('\nClassification Report:')
        self.stdout.write(classification_report(y_test, y_pred))

    def _get_training_data(self, data_days):
        """Get historical symptom and diagnosis data for training"""
        cutoff_date = datetime.now() - timedelta(days=data_days)
        
        # Get symptoms with confirmed diagnoses
        symptoms = Symptom.objects.filter(
            created_at__gte=cutoff_date,
            diagnosis__isnull=False,
            diagnosis__is_ai_generated=False  # Only use human-confirmed diagnoses
        ).select_related('patient')
        
        training_data = []
        
        for symptom in symptoms:
            # Get the first diagnosis for this symptom
            diagnosis = symptom.diagnosis_set.first()
            if not diagnosis or not diagnosis.preliminary_diagnosis:
                continue
            
            # Create training sample
            sample = {
                'text': symptom.description,
                'diagnosis': diagnosis.preliminary_diagnosis,
                'severity': symptom.severity,
                'patient_age': self._calculate_age(symptom.patient.date_of_birth) if symptom.patient.date_of_birth else None,
                'patient_gender': symptom.patient.gender,
                'input_method': symptom.input_method
            }
            training_data.append(sample)
        
        return training_data

    def _prepare_training_data(self, training_data):
        """Prepare features and labels for training"""
        X = []  # Features (symptom descriptions)
        y = []  # Labels (diagnoses)
        
        # Use symptom analyzer to get standardized diagnoses
        analyzer = SymptomAnalyzer()
        
        for sample in training_data:
            # Use the symptom text as features
            X.append(sample['text'])
            
            # Get standardized diagnosis using the analyzer
            severity, confidence, is_emergency, disease_predictions = analyzer.analyze_symptom(
                sample['text']
            )
            
            # Use the primary diagnosis as label
            primary_diagnosis = disease_predictions.get('primary_diagnosis', 'general_consultation')
            y.append(primary_diagnosis)
        
        return X, y

    def _create_model(self):
        """Create the ML pipeline"""
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=2,
                max_df=0.95
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            ))
        ])
        
        return pipeline

    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        return (datetime.now().date() - date_of_birth).days // 365
