#!/usr/bin/env python3
"""
Enhanced Dataset Creator for AI Healthcare Platform
==================================================

This script helps create a sophisticated dataset for symptom analysis
by combining multiple data sources and creating synthetic data for training.

Features:
- Load and process external medical datasets
- Generate synthetic symptom-disease mappings
- Create region-specific health data for Kenya/East Africa
- Validate and clean data for ML training
- Export data in formats compatible with your Django models

Usage:
    python enhance_dataset.py --action create_synthetic --samples 1000
    python enhance_dataset.py --action load_external --dataset ddxplus
    python enhance_dataset.py --action merge_all --output enhanced_dataset.json
"""

import json
import csv
import random
import pandas as pd
from datetime import datetime, timedelta
import argparse
from typing import List, Dict, Any
import requests
import os

class DatasetEnhancer:
    def __init__(self):
        """Initialize the dataset enhancer with regional health patterns"""
        
        # East African specific diseases and their prevalence
        self.regional_diseases = {
            'malaria': {
                'symptoms': [
                    'fever', 'chills', 'headache', 'nausea', 'vomiting', 'fatigue',
                    'muscle_aches', 'joint_pain', 'sweating', 'abdominal_pain'
                ],
                'prevalence': 0.15,  # 15% prevalence in the region
                'severity_distribution': {'low': 0.2, 'medium': 0.5, 'high': 0.25, 'critical': 0.05}
            },
            'tuberculosis': {
                'symptoms': [
                    'persistent_cough', 'chest_pain', 'fatigue', 'fever', 'night_sweats',
                    'weight_loss', 'loss_of_appetite', 'blood_in_sputum'
                ],
                'prevalence': 0.08,
                'severity_distribution': {'low': 0.1, 'medium': 0.4, 'high': 0.4, 'critical': 0.1}
            },
            'typhoid': {
                'symptoms': [
                    'high_fever', 'headache', 'abdominal_pain', 'diarrhea', 'constipation',
                    'fatigue', 'rash', 'nausea', 'vomiting'
                ],
                'prevalence': 0.06,
                'severity_distribution': {'low': 0.15, 'medium': 0.45, 'high': 0.35, 'critical': 0.05}
            },
            'respiratory_infection': {
                'symptoms': [
                    'cough', 'sore_throat', 'runny_nose', 'fever', 'headache',
                    'fatigue', 'body_aches', 'shortness_of_breath'
                ],
                'prevalence': 0.25,
                'severity_distribution': {'low': 0.4, 'medium': 0.4, 'high': 0.15, 'critical': 0.05}
            },
            'gastroenteritis': {
                'symptoms': [
                    'diarrhea', 'vomiting', 'nausea', 'abdominal_pain', 'fever',
                    'dehydration', 'loss_of_appetite', 'fatigue'
                ],
                'prevalence': 0.20,
                'severity_distribution': {'low': 0.3, 'medium': 0.4, 'high': 0.25, 'critical': 0.05}
            },
            'hypertension': {
                'symptoms': [
                    'headache', 'dizziness', 'chest_pain', 'shortness_of_breath',
                    'fatigue', 'irregular_heartbeat', 'nosebleeds'
                ],
                'prevalence': 0.12,
                'severity_distribution': {'low': 0.35, 'medium': 0.35, 'high': 0.25, 'critical': 0.05}
            },
            'diabetes': {
                'symptoms': [
                    'excessive_thirst', 'frequent_urination', 'fatigue', 'blurred_vision',
                    'slow_healing_wounds', 'weight_loss', 'increased_hunger'
                ],
                'prevalence': 0.10,
                'severity_distribution': {'low': 0.4, 'medium': 0.35, 'high': 0.2, 'critical': 0.05}
            }
        }
        
        # Swahili symptom translations
        self.swahili_translations = {
            'fever': ['homa', 'joto la mwili'],
            'headache': ['maumivu ya kichwa', 'kichwa kinauma'],
            'cough': ['kikohozi', 'kukohoa'],
            'nausea': ['kichefuchefu', 'hali ya kutapika'],
            'vomiting': ['kutapika', 'kupiga chura'],
            'diarrhea': ['kuhara', 'kupungua'],
            'fatigue': ['uchovu', 'kukosa nguvu'],
            'chest_pain': ['maumivu ya kifua', 'kifua kinauma'],
            'abdominal_pain': ['maumivu ya tumbo', 'tumbo linauma'],
            'shortness_of_breath': ['kupumua kwa shida', 'ukataji wa pumzi'],
            'dizziness': ['kizunguzungu', 'kichwa kinazunguka'],
            'joint_pain': ['maumivu ya viungo', 'viungo vynauma']
        }
        
        # Demographic patterns for Kenya
        self.demographic_patterns = {
            'age_groups': {
                '0-5': 0.18,    # Children
                '6-17': 0.22,   # Adolescents  
                '18-35': 0.32,  # Young adults
                '36-60': 0.20,  # Middle-aged
                '60+': 0.08     # Elderly
            },
            'gender_distribution': {
                'male': 0.49,
                'female': 0.51
            },
            'location_types': {
                'urban': 0.35,
                'rural': 0.65
            }
        }

    def create_synthetic_data(self, num_samples: int = 1000) -> List[Dict[str, Any]]:
        """Create synthetic symptom-disease data based on regional patterns"""
        
        print(f"Generating {num_samples} synthetic health records...")
        synthetic_data = []
        
        for i in range(num_samples):
            # Select disease based on prevalence
            disease = self._select_disease_by_prevalence()
            disease_info = self.regional_diseases[disease]
            
            # Generate patient demographics
            demographics = self._generate_demographics()
            
            # Generate symptoms for this disease
            symptoms = self._generate_symptoms_for_disease(disease, demographics)
            
            # Generate severity based on disease distribution
            severity = self._select_severity(disease_info['severity_distribution'])
            
            # Create record
            record = {
                'id': f"synthetic_{i+1:06d}",
                'patient_demographics': demographics,
                'symptoms_english': symptoms['english'],
                'symptoms_swahili': symptoms['swahili'],
                'primary_diagnosis': disease,
                'severity': severity,
                'confidence_score': random.uniform(0.7, 0.95),
                'is_emergency': severity in ['high', 'critical'],
                'created_at': self._random_date_within_year().isoformat(),
                'data_source': 'synthetic_regional'
            }
            
            synthetic_data.append(record)
        
        print(f"✅ Generated {len(synthetic_data)} synthetic records")
        return synthetic_data

    def load_ddxplus_dataset(self, file_path: str = None) -> List[Dict[str, Any]]:
        """Load and process DDXPlus dataset if available"""
        
        # DDXPlus dataset structure (if downloaded)
        ddxplus_data = []
        
        if file_path and os.path.exists(file_path):
            print(f"Loading DDXPlus dataset from {file_path}...")
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    record = {
                        'id': f"ddxplus_{row.get('PATIENT_ID', len(ddxplus_data))}",
                        'symptoms_english': [row.get('SYMPTOMS', '')],
                        'primary_diagnosis': row.get('DIAGNOSIS', 'general_consultation'),
                        'severity': self._map_severity(row.get('SEVERITY', 'medium')),
                        'confidence_score': 0.85,
                        'data_source': 'ddxplus'
                    }
                    ddxplus_data.append(record)
                    
                print(f"✅ Loaded {len(ddxplus_data)} records from DDXPlus")
            except Exception as e:
                print(f"❌ Error loading DDXPlus dataset: {e}")
        else:
            print("ℹ️ DDXPlus dataset not found. Create sample DDXPlus-style data...")
            # Create sample data in DDXPlus format
            ddxplus_data = self._create_ddxplus_sample()
        
        return ddxplus_data

    def create_comprehensive_dataset(self, synthetic_samples: int = 2000) -> Dict[str, Any]:
        """Create a comprehensive dataset combining all sources"""
        
        print("🚀 Creating comprehensive enhanced dataset...")
        
        # Generate synthetic data
        synthetic_data = self.create_synthetic_data(synthetic_samples)
        
        # Load external datasets
        ddxplus_data = self.load_ddxplus_dataset()
        
        # Combine all data sources
        all_data = synthetic_data + ddxplus_data
        
        # Create metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'total_samples': len(all_data),
            'data_sources': {
                'synthetic_regional': len(synthetic_data),
                'ddxplus': len(ddxplus_data)
            },
            'diseases_covered': list(self.regional_diseases.keys()),
            'languages': ['english', 'swahili'],
            'severity_levels': ['low', 'medium', 'high', 'critical'],
            'region_focus': 'East Africa (Kenya)',
            'quality_score': self._calculate_quality_score(all_data)
        }
        
        return {
            'metadata': metadata,
            'training_data': all_data
        }

    def export_for_django(self, dataset: Dict[str, Any], output_file: str = 'enhanced_training_data.json'):
        """Export dataset in Django-compatible format"""
        
        print(f"📤 Exporting dataset for Django to {output_file}...")
        
        # Convert to Django model format
        django_data = []
        
        for record in dataset['training_data']:
            # Create patient profile
            demographics = record.get('patient_demographics', {})
            
            django_record = {
                'model': 'backend.symptom',
                'fields': {
                    'description': ', '.join(record['symptoms_english']),
                    'severity': record['severity'],
                    'input_method': 'web',
                    'language': 'english',
                    'created_at': record.get('created_at', datetime.now().isoformat()),
                    # Patient info (you may need to create separate patient records)
                    'patient_age': demographics.get('age'),
                    'patient_gender': demographics.get('gender'),
                    'primary_diagnosis': record['primary_diagnosis'],
                    'confidence_score': record['confidence_score'],
                    'is_emergency': record.get('is_emergency', False),
                    'data_source': record.get('data_source', 'enhanced_dataset')
                }
            }
            django_record['pk'] = len(django_data) + 1
            django_data.append(django_record)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': dataset['metadata'],
                'fixtures': django_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(django_data)} records for Django")
        return output_file

    def _select_disease_by_prevalence(self) -> str:
        """Select a disease based on regional prevalence rates"""
        diseases = list(self.regional_diseases.keys())
        weights = [self.regional_diseases[d]['prevalence'] for d in diseases]
        return random.choices(diseases, weights=weights)[0]

    def _generate_demographics(self) -> Dict[str, Any]:
        """Generate realistic patient demographics for Kenya"""
        
        # Select age group
        age_group = random.choices(
            list(self.demographic_patterns['age_groups'].keys()),
            weights=list(self.demographic_patterns['age_groups'].values())
        )[0]
        
        # Generate specific age within group
        age_ranges = {
            '0-5': (0, 5),
            '6-17': (6, 17),
            '18-35': (18, 35),
            '36-60': (36, 60),
            '60+': (60, 85)
        }
        age = random.randint(*age_ranges[age_group])
        
        # Select gender
        gender = random.choices(
            ['male', 'female'],
            weights=[0.49, 0.51]
        )[0]
        
        # Select location type
        location_type = random.choices(
            ['urban', 'rural'],
            weights=[0.35, 0.65]
        )[0]
        
        return {
            'age': age,
            'age_group': age_group,
            'gender': gender,
            'location_type': location_type
        }

    def _generate_symptoms_for_disease(self, disease: str, demographics: Dict) -> Dict[str, List[str]]:
        """Generate realistic symptoms for a disease"""
        
        disease_info = self.regional_diseases[disease]
        available_symptoms = disease_info['symptoms']
        
        # Select 2-5 symptoms for this case
        num_symptoms = random.randint(2, min(5, len(available_symptoms)))
        selected_symptoms = random.sample(available_symptoms, num_symptoms)
        
        # Generate English descriptions
        english_symptoms = []
        swahili_symptoms = []
        
        for symptom in selected_symptoms:
            # English version with variations
            english_symptoms.append(self._add_symptom_variation(symptom, demographics))
            
            # Swahili translation if available
            if symptom in self.swahili_translations:
                swahili_variant = random.choice(self.swahili_translations[symptom])
                swahili_symptoms.append(swahili_variant)
        
        return {
            'english': english_symptoms,
            'swahili': swahili_symptoms
        }

    def _add_symptom_variation(self, symptom: str, demographics: Dict) -> str:
        """Add natural language variation to symptoms"""
        
        variations = {
            'fever': [
                'I have a fever', 'feeling feverish', 'high temperature',
                'my body feels hot', 'running a temperature'
            ],
            'headache': [
                'my head hurts', 'severe headache', 'head is pounding',
                'splitting headache', 'tension in my head'
            ],
            'cough': [
                'persistent cough', 'dry cough', 'coughing a lot',
                'can\'t stop coughing', 'productive cough'
            ],
            'fatigue': [
                'feeling tired', 'extremely exhausted', 'no energy',
                'feeling weak', 'constantly tired'
            ]
        }
        
        if symptom in variations:
            return random.choice(variations[symptom])
        else:
            return symptom.replace('_', ' ')

    def _select_severity(self, severity_distribution: Dict[str, float]) -> str:
        """Select severity based on disease-specific distribution"""
        
        severities = list(severity_distribution.keys())
        weights = list(severity_distribution.values())
        return random.choices(severities, weights=weights)[0]

    def _random_date_within_year(self) -> datetime:
        """Generate a random date within the last year"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        
        return start_date + timedelta(days=random_days)

    def _map_severity(self, external_severity: str) -> str:
        """Map external severity classifications to our system"""
        
        severity_mapping = {
            'mild': 'low',
            'moderate': 'medium', 
            'severe': 'high',
            'critical': 'critical',
            'emergency': 'critical'
        }
        
        return severity_mapping.get(external_severity.lower(), 'medium')

    def _create_ddxplus_sample(self) -> List[Dict[str, Any]]:
        """Create sample data in DDXPlus format when actual dataset isn't available"""
        
        sample_records = []
        
        # Create 100 sample records
        for i in range(100):
            disease = self._select_disease_by_prevalence()
            demographics = self._generate_demographics()
            symptoms = self._generate_symptoms_for_disease(disease, demographics)
            
            record = {
                'id': f"ddxplus_sample_{i+1}",
                'symptoms_english': symptoms['english'],
                'primary_diagnosis': disease,
                'severity': self._select_severity(self.regional_diseases[disease]['severity_distribution']),
                'confidence_score': 0.85,
                'data_source': 'ddxplus_sample'
            }
            sample_records.append(record)
        
        return sample_records

    def _calculate_quality_score(self, data: List[Dict]) -> float:
        """Calculate a quality score for the dataset"""
        
        if not data:
            return 0.0
        
        # Factors for quality assessment
        total_samples = len(data)
        unique_diagnoses = len(set(record['primary_diagnosis'] for record in data))
        avg_confidence = sum(record.get('confidence_score', 0) for record in data) / total_samples
        
        # Severity distribution balance
        severity_counts = {}
        for record in data:
            severity = record.get('severity', 'medium')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        severity_balance = 1.0 - (max(severity_counts.values()) / total_samples - 0.25) ** 2
        
        # Calculate overall quality score
        quality_score = (
            min(total_samples / 1000, 1.0) * 0.3 +  # Sample size
            min(unique_diagnoses / 10, 1.0) * 0.3 +  # Diagnosis diversity
            avg_confidence * 0.2 +                    # Confidence
            severity_balance * 0.2                    # Balance
        )
        
        return round(quality_score, 3)


def main():
    """Main function to handle command-line interface"""
    
    parser = argparse.ArgumentParser(
        description='Enhance AI Healthcare Platform dataset'
    )
    parser.add_argument(
        '--action',
        choices=['create_synthetic', 'load_external', 'merge_all'],
        default='merge_all',
        help='Action to perform'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=2000,
        help='Number of synthetic samples to generate'
    )
    parser.add_argument(
        '--output',
        default='enhanced_training_data.json',
        help='Output file name'
    )
    parser.add_argument(
        '--external-data',
        help='Path to external dataset file (e.g., DDXPlus CSV)'
    )
    
    args = parser.parse_args()
    
    enhancer = DatasetEnhancer()
    
    if args.action == 'create_synthetic':
        print("🔄 Creating synthetic dataset...")
        data = enhancer.create_synthetic_data(args.samples)
        with open(f'synthetic_{args.output}', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Synthetic dataset saved to synthetic_{args.output}")
        
    elif args.action == 'load_external':
        print("🔄 Loading external dataset...")
        data = enhancer.load_ddxplus_dataset(args.external_data)
        with open(f'external_{args.output}', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ External dataset saved to external_{args.output}")
        
    elif args.action == 'merge_all':
        print("🔄 Creating comprehensive enhanced dataset...")
        dataset = enhancer.create_comprehensive_dataset(args.samples)
        
        # Export for Django
        django_file = enhancer.export_for_django(dataset, args.output)
        
        # Also save raw dataset
        raw_output = f'raw_{args.output}'
        with open(raw_output, 'w') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 Enhanced dataset created successfully!")
        print(f"📊 Dataset Statistics:")
        print(f"   Total Samples: {dataset['metadata']['total_samples']}")
        print(f"   Diseases Covered: {len(dataset['metadata']['diseases_covered'])}")
        print(f"   Quality Score: {dataset['metadata']['quality_score']}")
        print(f"   Languages: {', '.join(dataset['metadata']['languages'])}")
        print(f"\n📁 Files Created:")
        print(f"   Django-ready: {django_file}")
        print(f"   Raw dataset: {raw_output}")


if __name__ == '__main__':
    main()
