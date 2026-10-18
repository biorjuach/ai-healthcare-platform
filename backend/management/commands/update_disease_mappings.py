from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os
from datetime import datetime, timedelta
from backend.models import Symptom, Diagnosis, Patient
from backend.ai_services import SymptomAnalyzer

class Command(BaseCommand):
    help = 'Update disease mappings based on historical data analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-days',
            type=int,
            default=365,
            help='Number of days of historical data to analyze'
        )
        parser.add_argument(
            '--min-occurrences',
            type=int,
            default=5,
            help='Minimum number of occurrences for a symptom-disease pair'
        )
        parser.add_argument(
            '--similarity-threshold',
            type=float,
            default=0.7,
            help='Similarity threshold for clustering similar symptoms'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            default='updated_disease_mappings.json',
            help='Output file for updated mappings'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting disease mapping analysis...')
        
        # Get historical data
        training_data = self._get_historical_data(options['data_days'])
        
        if not training_data:
            self.stdout.write(
                self.style.WARNING('No historical data found for analysis')
            )
            return
        
        self.stdout.write(f'Analyzing {len(training_data)} symptom-diagnosis pairs...')
        
        # Analyze symptom-disease patterns
        symptom_disease_patterns = self._analyze_patterns(training_data)
        
        # Generate updated mappings
        updated_mappings = self._generate_updated_mappings(
            symptom_disease_patterns, 
            options['min_occurrences']
        )
        
        # Analyze symptom clusters
        symptom_clusters = self._analyze_symptom_clusters(training_data, options['similarity_threshold'])
        
        # Create comprehensive mapping update
        mapping_update = {
            'updated_at': datetime.now().isoformat(),
            'data_period_days': options['data_days'],
            'total_samples': len(training_data),
            'symptom_disease_mapping': updated_mappings,
            'symptom_clusters': symptom_clusters,
            'statistics': self._generate_statistics(training_data)
        }
        
        # Save updated mappings
        output_path = os.path.join('models', options['output_file'])
        os.makedirs('models', exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(mapping_update, f, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated disease mappings saved to {output_path}'
            )
        )
        
        # Print summary
        self._print_summary(mapping_update)

    def _get_historical_data(self, data_days):
        """Get historical symptom-diagnosis data"""
        cutoff_date = datetime.now() - timedelta(days=data_days)
        
        symptoms = Symptom.objects.filter(
            created_at__gte=cutoff_date,
            diagnosis__isnull=False
        ).select_related('patient')
        
        data = []
        for symptom in symptoms:
            diagnosis = symptom.diagnosis_set.first()
            if diagnosis and diagnosis.preliminary_diagnosis:
                data.append({
                    'symptom_text': symptom.description.lower(),
                    'diagnosis': diagnosis.preliminary_diagnosis,
                    'severity': symptom.severity,
                    'confidence': diagnosis.confidence_score,
                    'patient_age': self._calculate_age(symptom.patient.date_of_birth) if symptom.patient.date_of_birth else None,
                    'patient_gender': symptom.patient.gender
                })
        
        return data

    def _analyze_patterns(self, data):
        """Analyze symptom-disease patterns"""
        patterns = {}
        
        for item in data:
            symptom_text = item['symptom_text']
            diagnosis = item['diagnosis']
            
            # Extract key symptoms from text
            key_symptoms = self._extract_key_symptoms(symptom_text)
            
            for symptom in key_symptoms:
                if symptom not in patterns:
                    patterns[symptom] = {}
                
                if diagnosis not in patterns[symptom]:
                    patterns[symptom][diagnosis] = {
                        'count': 0,
                        'total_confidence': 0,
                        'severities': [],
                        'ages': [],
                        'genders': []
                    }
                
                patterns[symptom][diagnosis]['count'] += 1
                patterns[symptom][diagnosis]['total_confidence'] += item['confidence']
                patterns[symptom][diagnosis]['severities'].append(item['severity'])
                
                if item['patient_age']:
                    patterns[symptom][diagnosis]['ages'].append(item['patient_age'])
                
                if item['patient_gender']:
                    patterns[symptom][diagnosis]['genders'].append(item['patient_gender'])
        
        return patterns

    def _extract_key_symptoms(self, text):
        """Extract key symptoms from text"""
        # Use the existing symptom analyzer's mappings
        analyzer = SymptomAnalyzer()
        key_symptoms = []
        
        for symptom in analyzer.symptom_disease_mapping.keys():
            if symptom in text or symptom.replace('_', ' ') in text:
                key_symptoms.append(symptom)
        
        # Add common symptom variations
        symptom_variations = {
            'fever': ['fever', 'temperature', 'hot', 'burning'],
            'cough': ['cough', 'coughing', 'dry cough', 'wet cough'],
            'headache': ['headache', 'head pain', 'migraine'],
            'chest_pain': ['chest pain', 'chest discomfort', 'heart pain'],
            'abdominal_pain': ['stomach pain', 'abdominal pain', 'tummy ache', 'belly pain'],
            'nausea': ['nausea', 'sick', 'queasy'],
            'vomiting': ['vomiting', 'throwing up', 'puking'],
            'diarrhea': ['diarrhea', 'loose stools', 'running stomach'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak']
        }
        
        for symptom, variations in symptom_variations.items():
            if any(var in text for var in variations):
                key_symptoms.append(symptom)
        
        return list(set(key_symptoms))

    def _generate_updated_mappings(self, patterns, min_occurrences):
        """Generate updated symptom-disease mappings"""
        updated_mappings = {}
        
        for symptom, diseases in patterns.items():
            # Filter diseases by minimum occurrences
            filtered_diseases = {
                disease: data for disease, data in diseases.items() 
                if data['count'] >= min_occurrences
            }
            
            if not filtered_diseases:
                continue
            
            # Calculate weights based on frequency and confidence
            total_cases = sum(data['count'] for data in filtered_diseases.values())
            total_confidence = sum(data['total_confidence'] for data in filtered_diseases.values())
            
            diseases_list = []
            weights_list = []
            
            for disease, data in filtered_diseases.items():
                diseases_list.append(disease)
                
                # Weight based on frequency and average confidence
                frequency_weight = data['count'] / total_cases
                avg_confidence = data['total_confidence'] / data['count'] if data['count'] > 0 else 0
                combined_weight = (frequency_weight * 0.7) + (avg_confidence * 0.3)
                weights_list.append(combined_weight)
            
            # Normalize weights
            if weights_list:
                total_weight = sum(weights_list)
                weights_list = [w / total_weight for w in weights_list]
            
            # Calculate average severity
            all_severities = []
            for data in filtered_diseases.values():
                all_severities.extend(data['severities'])
            avg_severity = np.mean(all_severities) if all_severities else 0.5
            
            updated_mappings[symptom] = {
                'diseases': diseases_list,
                'weights': weights_list,
                'severity': avg_severity,
                'total_cases': total_cases,
                'avg_confidence': total_confidence / total_cases if total_cases > 0 else 0
            }
        
        return updated_mappings

    def _analyze_symptom_clusters(self, data, similarity_threshold):
        """Analyze symptom clusters using text similarity"""
        if len(data) < 2:
            return {}
        
        # Extract symptom texts
        texts = [item['symptom_text'] for item in data]
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find clusters
            clusters = self._find_similarity_clusters(similarity_matrix, similarity_threshold)
            
            # Group symptoms by clusters
            symptom_clusters = {}
            for cluster_id, indices in clusters.items():
                cluster_symptoms = [texts[i] for i in indices]
                cluster_diagnoses = [data[i]['diagnosis'] for i in indices]
                
                symptom_clusters[f'cluster_{cluster_id}'] = {
                    'symptoms': cluster_symptoms,
                    'diagnoses': cluster_diagnoses,
                    'size': len(indices)
                }
            
            return symptom_clusters
            
        except Exception as e:
            self.stdout.write(f'Warning: Could not perform clustering analysis: {e}')
            return {}

    def _find_similarity_clusters(self, similarity_matrix, threshold):
        """Find clusters based on similarity threshold"""
        clusters = {}
        cluster_id = 0
        used_indices = set()
        
        for i in range(len(similarity_matrix)):
            if i in used_indices:
                continue
            
            # Find all similar items
            similar_indices = [i]
            used_indices.add(i)
            
            for j in range(i + 1, len(similarity_matrix)):
                if j not in used_indices and similarity_matrix[i][j] >= threshold:
                    similar_indices.append(j)
                    used_indices.add(j)
            
            if len(similar_indices) > 1:  # Only keep clusters with multiple items
                clusters[cluster_id] = similar_indices
                cluster_id += 1
        
        return clusters

    def _generate_statistics(self, data):
        """Generate statistics about the data"""
        total_cases = len(data)
        unique_symptoms = len(set(item['symptom_text'] for item in data))
        unique_diagnoses = len(set(item['diagnosis'] for item in data))
        
        # Convert severity strings to numeric values
        severity_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        severities = [severity_mapping.get(item['severity'], 1) for item in data if item['severity']]
        avg_severity = np.mean(severities) if severities else 0
        
        confidences = [item['confidence'] for item in data if item['confidence']]
        avg_confidence = np.mean(confidences) if confidences else 0
        
        ages = [item['patient_age'] for item in data if item['patient_age']]
        avg_age = np.mean(ages) if ages else 0
        
        gender_distribution = {}
        for item in data:
            if item['patient_gender']:
                gender = item['patient_gender']
                gender_distribution[gender] = gender_distribution.get(gender, 0) + 1
        
        return {
            'total_cases': total_cases,
            'unique_symptoms': unique_symptoms,
            'unique_diagnoses': unique_diagnoses,
            'average_severity': avg_severity,
            'average_confidence': avg_confidence,
            'average_patient_age': avg_age,
            'gender_distribution': gender_distribution
        }

    def _print_summary(self, mapping_update):
        """Print summary of the analysis"""
        stats = mapping_update['statistics']
        
        self.stdout.write('\n=== Analysis Summary ===')
        self.stdout.write(f'Total cases analyzed: {stats["total_cases"]}')
        self.stdout.write(f'Unique symptoms found: {stats["unique_symptoms"]}')
        self.stdout.write(f'Unique diagnoses found: {stats["unique_diagnoses"]}')
        self.stdout.write(f'Average severity: {stats["average_severity"]:.2f}')
        self.stdout.write(f'Average confidence: {stats["average_confidence"]:.2f}')
        self.stdout.write(f'Average patient age: {stats["average_patient_age"]:.1f}')
        
        self.stdout.write(f'\nSymptom-disease mappings updated: {len(mapping_update["symptom_disease_mapping"])}')
        self.stdout.write(f'Symptom clusters found: {len(mapping_update["symptom_clusters"])}')

    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        return (datetime.now().date() - date_of_birth).days // 365
