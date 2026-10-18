from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import pickle
import os
import json
import numpy as np
from datetime import datetime, timedelta
from backend.models import Symptom, Diagnosis, Patient, MedicalRecord

class Command(BaseCommand):
    help = 'Retrain models using doctor feedback and patient outcomes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feedback-days',
            type=int,
            default=30,
            help='Number of days of feedback data to use for retraining'
        )
        parser.add_argument(
            '--min-feedback-samples',
            type=int,
            default=20,
            help='Minimum number of feedback samples required for retraining'
        )
        parser.add_argument(
            '--improvement-threshold',
            type=float,
            default=0.02,
            help='Minimum accuracy improvement required to deploy new model'
        )
        parser.add_argument(
            '--backup-existing',
            action='store_true',
            help='Backup existing model before retraining'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting model retraining with feedback...')
        
        # Get feedback data
        feedback_data = self._get_feedback_data(options['feedback_days'])
        
        if len(feedback_data) < options['min_feedback_samples']:
            self.stdout.write(
                self.style.WARNING(
                    f'Insufficient feedback data. Found {len(feedback_data)} samples, '
                    f'minimum required: {options["min_feedback_samples"]}'
                )
            )
            return
        
        self.stdout.write(f'Using {len(feedback_data)} feedback samples for retraining...')
        
        # Backup existing model if requested
        if options['backup_existing']:
            self._backup_existing_model()
        
        # Prepare training data with feedback
        X_train, y_train, feedback_weights = self._prepare_feedback_data(feedback_data)
        
        # Create and train new model
        new_model = self._create_enhanced_model()
        
        self.stdout.write('Training new model with feedback...')
        new_model.fit(X_train, y_train, sample_weight=feedback_weights)
        
        # Evaluate new model
        new_accuracy = self._evaluate_model(new_model, X_train, y_train)
        
        # Compare with existing model
        existing_accuracy = self._evaluate_existing_model(X_train, y_train)
        
        improvement = new_accuracy - existing_accuracy
        
        self.stdout.write(f'Existing model accuracy: {existing_accuracy:.3f}')
        self.stdout.write(f'New model accuracy: {new_accuracy:.3f}')
        self.stdout.write(f'Improvement: {improvement:.3f}')
        
        # Deploy new model if improvement is significant
        if improvement >= options['improvement_threshold']:
            self._deploy_new_model(new_model, new_accuracy, improvement)
            self.stdout.write(
                self.style.SUCCESS(
                    f'New model deployed successfully! Improvement: {improvement:.3f}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Improvement ({improvement:.3f}) below threshold ({options["improvement_threshold"]}). '
                    'Keeping existing model.'
                )
            )

    def _get_feedback_data(self, feedback_days):
        """Get feedback data from doctors and patient outcomes"""
        cutoff_date = datetime.now() - timedelta(days=feedback_days)
        
        # Get symptoms with doctor feedback (confirmed diagnoses)
        symptoms_with_feedback = Symptom.objects.filter(
            created_at__gte=cutoff_date,
            diagnosis__isnull=False,
            diagnosis__is_ai_generated=True,  # AI-generated diagnoses that were reviewed
            diagnosis__doctor__isnull=False   # Doctor confirmed the diagnosis
        ).select_related('patient')
        
        # Get medical records with outcomes
        medical_records = MedicalRecord.objects.filter(
            created_at__gte=cutoff_date,
            diagnosis__isnull=False
        ).select_related('patient')
        
        feedback_data = []
        
        # Process symptoms with doctor feedback
        for symptom in symptoms_with_feedback:
            diagnosis = symptom.diagnosis_set.first()
            if not diagnosis:
                continue
                
            feedback_score = self._calculate_feedback_score(symptom, diagnosis)
            
            feedback_data.append({
                'text': symptom.description,
                'ai_diagnosis': diagnosis.preliminary_diagnosis,
                'doctor_diagnosis': diagnosis.preliminary_diagnosis,  # Doctor confirmed
                'feedback_score': feedback_score,
                'feedback_type': 'doctor_confirmation',
                'severity': symptom.severity,
                'patient_age': self._calculate_age(symptom.patient.date_of_birth) if symptom.patient.date_of_birth else None,
                'patient_gender': symptom.patient.gender
            })
        
        # Process medical records with outcomes
        for record in medical_records:
            diagnosis = record.diagnosis_set.first()
            if not diagnosis:
                continue
                
            outcome_score = self._calculate_outcome_score(record)
            
            feedback_data.append({
                'text': diagnosis.symptom.description if diagnosis.symptom else '',
                'ai_diagnosis': diagnosis.preliminary_diagnosis,
                'final_diagnosis': diagnosis.preliminary_diagnosis,  # Final diagnosis
                'feedback_score': outcome_score,
                'feedback_type': 'treatment_outcome',
                'treatment_success': self._assess_treatment_success(record),
                'patient_age': self._calculate_age(record.patient.date_of_birth) if record.patient.date_of_birth else None,
                'patient_gender': record.patient.gender
            })
        
        return feedback_data

    def _calculate_feedback_score(self, symptom, diagnosis):
        """Calculate feedback score based on doctor confirmation"""
        # Base score for doctor confirmation
        score = 1.0
        
        # Boost score if doctor has high confidence
        if diagnosis.confidence_score > 0.8:
            score += 0.2
        
        # Boost score if doctor is a specialist
        doctor = diagnosis.doctor
        if doctor and doctor.specialization != 'general':
            score += 0.1
        
        # Boost score if doctor has more experience
        if doctor and doctor.years_of_experience > 10:
            score += 0.1
        
        return min(score, 2.0)  # Cap at 2.0

    def _calculate_outcome_score(self, medical_record):
        """Calculate feedback score based on treatment outcome"""
        # Base score
        score = 1.0
        
        # Boost score if treatment was successful
        if self._assess_treatment_success(medical_record):
            score += 0.3
        
        # Boost score if follow-up was not required (indicating successful treatment)
        if not medical_record.follow_up_required:
            score += 0.2
        
        # Reduce score if abnormal test results
        if hasattr(medical_record, 'testresult_set'):
            abnormal_tests = medical_record.testresult_set.filter(is_abnormal=True).count()
            if abnormal_tests > 0:
                score -= 0.1 * abnormal_tests
        
        return max(score, 0.5)  # Minimum score of 0.5

    def _assess_treatment_success(self, medical_record):
        """Assess if treatment was successful based on medical record"""
        # Check if follow-up was required
        if medical_record.follow_up_required:
            return False
        
        # Check for positive treatment notes
        positive_indicators = ['improved', 'better', 'resolved', 'cured', 'healed', 'recovered']
        negative_indicators = ['worse', 'deteriorated', 'failed', 'complication', 'relapse']
        
        notes_lower = medical_record.notes.lower()
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in notes_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in notes_lower)
        
        return positive_count > negative_count

    def _prepare_feedback_data(self, feedback_data):
        """Prepare training data with feedback weights"""
        X_train = []
        y_train = []
        feedback_weights = []
        
        for item in feedback_data:
            if item['text']:  # Only include items with symptom text
                X_train.append(item['text'])
                
                # Use the final diagnosis as the target
                final_diagnosis = item.get('final_diagnosis', item.get('doctor_diagnosis', item['ai_diagnosis']))
                y_train.append(final_diagnosis)
                
                # Use feedback score as sample weight
                feedback_weights.append(item['feedback_score'])
        
        return X_train, y_train, feedback_weights

    def _create_enhanced_model(self):
        """Create an enhanced model for retraining"""
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1500,  # Increased features
                ngram_range=(1, 3),  # Include trigrams
                stop_words='english',
                min_df=2,
                max_df=0.9
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=150,  # More trees
                max_depth=15,      # Deeper trees
                random_state=42,
                class_weight='balanced',
                min_samples_split=5,
                min_samples_leaf=2
            ))
        ])
        
        return pipeline

    def _evaluate_model(self, model, X, y):
        """Evaluate model performance"""
        try:
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5)
            return cv_scores.mean()
        except Exception as e:
            self.stdout.write(f'Error evaluating model: {e}')
            return 0.0

    def _evaluate_existing_model(self, X, y):
        """Evaluate existing model performance"""
        model_path = 'models/symptom_classifier.pkl'
        
        if not os.path.exists(model_path):
            return 0.0
        
        try:
            with open(model_path, 'rb') as f:
                existing_model = pickle.load(f)
            
            return self._evaluate_model(existing_model, X, y)
        except Exception as e:
            self.stdout.write(f'Error evaluating existing model: {e}')
            return 0.0

    def _backup_existing_model(self):
        """Backup existing model"""
        model_path = 'models/symptom_classifier.pkl'
        metadata_path = 'models/symptom_classifier_metadata.json'
        
        if os.path.exists(model_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = 'models/backups'
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Backup model
            backup_model_path = os.path.join(backup_dir, f'symptom_classifier_backup_{timestamp}.pkl')
            with open(model_path, 'rb') as src, open(backup_model_path, 'wb') as dst:
                dst.write(src.read())
            
            # Backup metadata
            if os.path.exists(metadata_path):
                backup_metadata_path = os.path.join(backup_dir, f'symptom_classifier_metadata_backup_{timestamp}.json')
                with open(metadata_path, 'r') as src, open(backup_metadata_path, 'w') as dst:
                    dst.write(src.read())
            
            self.stdout.write(f'Existing model backed up to {backup_dir}')

    def _deploy_new_model(self, model, accuracy, improvement):
        """Deploy the new model"""
        # Create models directory if it doesn't exist
        models_dir = 'models'
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        
        # Save new model
        model_path = os.path.join(models_dir, 'symptom_classifier.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Update metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'accuracy': accuracy,
            'improvement': improvement,
            'training_method': 'feedback_retraining',
            'feature_names': model.named_steps['tfidf'].get_feature_names_out().tolist() if hasattr(model.named_steps['tfidf'], 'get_feature_names_out') else []
        }
        
        metadata_path = os.path.join(models_dir, 'symptom_classifier_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.stdout.write(f'New model deployed to {model_path}')

    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        return (datetime.now().date() - date_of_birth).days // 365
