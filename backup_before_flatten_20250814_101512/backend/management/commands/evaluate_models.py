from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import cross_val_score
import pickle
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from backend.models import Symptom, Diagnosis, Patient
from backend.ai_services import SymptomAnalyzer

class Command(BaseCommand):
    help = 'Evaluate model performance and generate reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-path',
            type=str,
            default='models/symptom_classifier.pkl',
            help='Path to the trained model file'
        )
        parser.add_argument(
            '--test-days',
            type=int,
            default=30,
            help='Number of days of recent data to use for testing'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='reports',
            help='Directory to save evaluation reports'
        )
        parser.add_argument(
            '--compare-baseline',
            action='store_true',
            help='Compare ML model with rule-based baseline'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting model evaluation...')
        
        # Create output directory
        output_dir = options['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(f'Created output directory: {output_dir}')
        
        # Check if model exists
        model_path = options['model_path']
        if not os.path.exists(model_path):
            self.stdout.write(
                self.style.WARNING(f'Model file not found: {model_path}')
            )
            return
        
        # Load model
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            self.stdout.write(f'Loaded model from: {model_path}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading model: {e}')
            )
            return
        
        # Get test data
        test_data = self._get_test_data(options['test_days'])
        
        if not test_data:
            self.stdout.write(
                self.style.WARNING('No test data found')
            )
            return
        
        self.stdout.write(f'Evaluating on {len(test_data)} test samples...')
        
        # Prepare test data
        X_test, y_true = self._prepare_test_data(test_data)
        
        # Evaluate ML model
        ml_results = self._evaluate_ml_model(model, X_test, y_true)
        
        # Compare with baseline if requested
        baseline_results = None
        if options['compare_baseline']:
            baseline_results = self._evaluate_baseline(test_data)
        
        # Generate comprehensive report
        report = self._generate_report(ml_results, baseline_results, test_data)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(output_dir, f'model_evaluation_{timestamp}.json')
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save detailed metrics
        metrics_path = os.path.join(output_dir, f'detailed_metrics_{timestamp}.json')
        with open(metrics_path, 'w') as f:
            json.dump(ml_results, f, indent=2)
        
        # Print summary
        self._print_summary(report)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Evaluation complete. Reports saved to {output_dir}'
            )
        )

    def _get_test_data(self, test_days):
        """Get recent data for testing"""
        cutoff_date = datetime.now() - timedelta(days=test_days)
        
        symptoms = Symptom.objects.filter(
            created_at__gte=cutoff_date,
            diagnosis__isnull=False
        ).select_related('patient')
        
        test_data = []
        for symptom in symptoms:
            diagnosis = symptom.diagnosis_set.first()
            if diagnosis and diagnosis.preliminary_diagnosis:
                test_data.append({
                    'text': symptom.description,
                    'diagnosis': diagnosis.preliminary_diagnosis,
                    'severity': symptom.severity,
                    'confidence': diagnosis.confidence_score,
                    'is_ai_generated': diagnosis.is_ai_generated,
                    'patient_age': self._calculate_age(symptom.patient.date_of_birth) if symptom.patient.date_of_birth else None,
                    'patient_gender': symptom.patient.gender,
                    'input_method': symptom.input_method,
                    'created_at': symptom.created_at
                })
        
        return test_data

    def _prepare_test_data(self, test_data):
        """Prepare test data for evaluation"""
        X_test = []
        y_true = []
        
        analyzer = SymptomAnalyzer()
        
        for item in test_data:
            X_test.append(item['text'])
            
            # Get standardized diagnosis
            severity, confidence, is_emergency, disease_predictions = analyzer.analyze_symptom(
                item['text']
            )
            primary_diagnosis = disease_predictions.get('primary_diagnosis', 'general_consultation')
            y_true.append(primary_diagnosis)
        
        return X_test, y_true

    def _evaluate_ml_model(self, model, X_test, y_true):
        """Evaluate the ML model"""
        try:
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision, recall, f1, support = precision_recall_fscore_support(
                y_true, y_pred, average='weighted'
            )
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_test, y_true, cv=5)
            
            # Per-class metrics
            class_report = classification_report(y_true, y_pred, output_dict=True)
            
            # Confidence analysis
            confidence_analysis = self._analyze_confidence(y_pred_proba, y_true, y_pred)
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'support': support,
                'confusion_matrix': cm.tolist(),
                'cv_scores': {
                    'mean': cv_scores.mean(),
                    'std': cv_scores.std(),
                    'scores': cv_scores.tolist()
                },
                'classification_report': class_report,
                'confidence_analysis': confidence_analysis,
                'predictions': y_pred,
                'true_labels': y_true
            }
            
        except Exception as e:
            self.stdout.write(f'Error evaluating ML model: {e}')
            return None

    def _evaluate_baseline(self, test_data):
        """Evaluate rule-based baseline"""
        analyzer = SymptomAnalyzer()
        
        y_true = []
        y_pred = []
        confidences = []
        
        for item in test_data:
            # Get baseline prediction
            severity, confidence, is_emergency, disease_predictions = analyzer.analyze_symptom(
                item['text']
            )
            
            primary_diagnosis = disease_predictions.get('primary_diagnosis', 'general_consultation')
            y_pred.append(primary_diagnosis)
            
            # Get true diagnosis
            true_diagnosis = item['diagnosis']
            y_true.append(true_diagnosis)
            
            confidences.append(confidence)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'support': support,
            'average_confidence': np.mean(confidences),
            'predictions': y_pred,
            'true_labels': y_true
        }

    def _analyze_confidence(self, y_pred_proba, y_true, y_pred):
        """Analyze prediction confidence"""
        if y_pred_proba is None:
            return None
        
        # Calculate confidence scores
        confidence_scores = np.max(y_pred_proba, axis=1)
        
        # Analyze confidence vs accuracy
        correct_predictions = np.array(y_true) == np.array(y_pred)
        
        # Group by confidence levels
        confidence_bins = [0.0, 0.5, 0.7, 0.8, 0.9, 1.0]
        confidence_analysis = {}
        
        for i in range(len(confidence_bins) - 1):
            low, high = confidence_bins[i], confidence_bins[i + 1]
            mask = (confidence_scores >= low) & (confidence_scores < high)
            
            if np.sum(mask) > 0:
                bin_accuracy = np.mean(correct_predictions[mask])
                bin_count = np.sum(mask)
                
                confidence_analysis[f'{low:.1f}-{high:.1f}'] = {
                    'accuracy': bin_accuracy,
                    'count': bin_count,
                    'avg_confidence': np.mean(confidence_scores[mask])
                }
        
        return {
            'overall_avg_confidence': np.mean(confidence_scores),
            'confidence_vs_accuracy': confidence_analysis,
            'high_confidence_accuracy': np.mean(correct_predictions[confidence_scores >= 0.8])
        }

    def _generate_report(self, ml_results, baseline_results, test_data):
        """Generate comprehensive evaluation report"""
        report = {
            'evaluation_date': datetime.now().isoformat(),
            'test_data_summary': {
                'total_samples': len(test_data),
                'unique_diagnoses': len(set(item['diagnosis'] for item in test_data)),
                'date_range': {
                    'start': min(item['created_at'] for item in test_data).isoformat(),
                    'end': max(item['created_at'] for item in test_data).isoformat()
                }
            },
            'ml_model_results': ml_results,
            'baseline_comparison': baseline_results,
            'recommendations': []
        }
        
        # Generate recommendations
        if ml_results and baseline_results:
            ml_accuracy = ml_results['accuracy']
            baseline_accuracy = baseline_results['accuracy']
            
            if ml_accuracy > baseline_accuracy:
                improvement = ((ml_accuracy - baseline_accuracy) / baseline_accuracy) * 100
                report['recommendations'].append({
                    'type': 'success',
                    'message': f'ML model outperforms baseline by {improvement:.1f}%'
                })
            else:
                report['recommendations'].append({
                    'type': 'warning',
                    'message': 'ML model does not outperform baseline. Consider retraining with more data.'
                })
        
        if ml_results and ml_results['accuracy'] < 0.7:
            report['recommendations'].append({
                'type': 'warning',
                'message': 'Model accuracy below 70%. Consider collecting more training data.'
            })
        
        if ml_results and ml_results['cv_scores']['std'] > 0.1:
            report['recommendations'].append({
                'type': 'warning',
                'message': 'High cross-validation variance. Model may be overfitting.'
            })
        
        return report

    def _print_summary(self, report):
        """Print evaluation summary"""
        self.stdout.write('\n=== Model Evaluation Summary ===')
        
        if report['ml_model_results']:
            ml_results = report['ml_model_results']
            self.stdout.write(f'ML Model Accuracy: {ml_results["accuracy"]:.3f}')
            self.stdout.write(f'ML Model F1-Score: {ml_results["f1_score"]:.3f}')
            self.stdout.write(f'Cross-validation: {ml_results["cv_scores"]["mean"]:.3f} (+/- {ml_results["cv_scores"]["std"]*2:.3f})')
        
        if report['baseline_comparison']:
            baseline = report['baseline_comparison']
            self.stdout.write(f'Baseline Accuracy: {baseline["accuracy"]:.3f}')
            self.stdout.write(f'Baseline F1-Score: {baseline["f1_score"]:.3f}')
        
        self.stdout.write(f'\nTest samples: {report["test_data_summary"]["total_samples"]}')
        self.stdout.write(f'Unique diagnoses: {report["test_data_summary"]["unique_diagnoses"]}')
        
        if report['recommendations']:
            self.stdout.write('\n=== Recommendations ===')
            for rec in report['recommendations']:
                style = getattr(self.style, rec['type'].upper(), self.style.WARNING)
                self.stdout.write(style(rec['message']))

    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        return (datetime.now().date() - date_of_birth).days // 365
