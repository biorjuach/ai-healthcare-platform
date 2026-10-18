#!/usr/bin/env python3
"""
CSV Dataset Loader for AI Healthcare Platform
============================================

This script loads your existing CSV dataset directly into the system
for training the symptom analysis ML model.

Supports various CSV formats and automatically maps columns to your system.

Usage:
    python load_csv_dataset.py --csv-file your_dataset.csv --preview
    python load_csv_dataset.py --csv-file your_dataset.csv --load
"""

import pandas as pd
import json
import argparse
from datetime import datetime
import os
import sys

class CSVDatasetLoader:
    def __init__(self):
        """Initialize the CSV dataset loader"""
        
        # Common column name mappings
        self.column_mappings = {
            'symptoms': [
                'symptoms', 'symptom', 'description', 'patient_symptoms', 
                'symptom_description', 'complaints', 'chief_complaint',
                'presenting_symptoms', 'clinical_symptoms', 'text'
            ],
            'diagnosis': [
                'diagnosis', 'disease', 'condition', 'primary_diagnosis',
                'final_diagnosis', 'medical_diagnosis', 'label', 'class',
                'target', 'disease_name', 'prognosis'
            ],
            'severity': [
                'severity', 'urgency', 'priority', 'triage_level',
                'emergency_level', 'acuity', 'risk_level'
            ],
            'age': [
                'age', 'patient_age', 'age_years', 'years_old'
            ],
            'gender': [
                'gender', 'sex', 'patient_gender', 'patient_sex'
            ],
            'duration': [
                'duration', 'symptom_duration', 'time_since_onset',
                'days_with_symptoms', 'duration_days'
            ]
        }
        
        # Severity mappings from various formats
        self.severity_mappings = {
            # Numeric scales
            '1': 'low', '2': 'medium', '3': 'high', '4': 'critical',
            1: 'low', 2: 'medium', 3: 'high', 4: 'critical',
            # Text variations
            'mild': 'low', 'moderate': 'medium', 'severe': 'high',
            'critical': 'critical', 'emergency': 'critical',
            'low': 'low', 'medium': 'medium', 'high': 'high',
            'urgent': 'high', 'non-urgent': 'low',
            # Triage levels
            'triage_1': 'critical', 'triage_2': 'high', 
            'triage_3': 'medium', 'triage_4': 'low', 'triage_5': 'low'
        }

    def analyze_csv(self, csv_file: str) -> dict:
        """Analyze CSV structure and suggest column mappings"""
        
        print(f"📊 Analyzing CSV file: {csv_file}")
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    print(f"✅ Successfully loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Could not read CSV with any encoding")
                
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return None
        
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'sample_data': df.head().to_dict('records'),
            'suggested_mappings': {},
            'data_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict()
        }
        
        # Suggest column mappings
        for field, possible_names in self.column_mappings.items():
            for col in df.columns:
                if col.lower() in [name.lower() for name in possible_names]:
                    analysis['suggested_mappings'][field] = col
                    break
        
        return analysis

    def preview_data(self, csv_file: str, custom_mappings: dict = None) -> dict:
        """Preview how the data will be processed"""
        
        analysis = self.analyze_csv(csv_file)
        if not analysis:
            return None
        
        df = pd.read_csv(csv_file)
        
        # Use custom mappings or suggested ones
        mappings = custom_mappings or analysis['suggested_mappings']
        
        print(f"\n📋 Data Preview (first 5 rows):")
        print("=" * 80)
        
        preview_data = []
        for idx, row in df.head().iterrows():
            processed_row = self._process_row(row, mappings)
            preview_data.append(processed_row)
            
            print(f"Row {idx + 1}:")
            print(f"  Symptoms: {processed_row.get('symptoms', 'N/A')}")
            print(f"  Diagnosis: {processed_row.get('diagnosis', 'N/A')}")
            print(f"  Severity: {processed_row.get('severity', 'N/A')}")
            if processed_row.get('demographics'):
                demo = processed_row['demographics']
                print(f"  Age: {demo.get('age', 'N/A')}, Gender: {demo.get('gender', 'N/A')}")
            print("-" * 40)
        
        return {
            'preview_data': preview_data,
            'total_rows': len(df),
            'mappings_used': mappings,
            'issues_found': self._identify_issues(df, mappings)
        }

    def convert_to_enhanced_format(self, csv_file: str, output_file: str = None, 
                                  custom_mappings: dict = None) -> str:
        """Convert CSV to enhanced dataset format"""
        
        print(f"🔄 Converting CSV to enhanced dataset format...")
        
        analysis = self.analyze_csv(csv_file)
        if not analysis:
            return None
        
        df = pd.read_csv(csv_file)
        mappings = custom_mappings or analysis['suggested_mappings']
        
        # Process all rows
        enhanced_data = []
        for idx, row in df.iterrows():
            try:
                processed_row = self._process_row(row, mappings)
                if processed_row.get('symptoms') and processed_row.get('diagnosis'):
                    enhanced_data.append(processed_row)
            except Exception as e:
                print(f"⚠️ Error processing row {idx}: {e}")
                continue
        
        # Create dataset structure
        dataset = {
            'metadata': {
                'source_file': csv_file,
                'created_at': datetime.now().isoformat(),
                'total_samples': len(enhanced_data),
                'original_rows': len(df),
                'success_rate': len(enhanced_data) / len(df) if len(df) > 0 else 0,
                'column_mappings': mappings,
                'data_source': 'user_csv',
                'quality_score': self._calculate_quality_score(enhanced_data)
            },
            'training_data': enhanced_data
        }
        
        # Save to file
        if not output_file:
            output_file = f"converted_{os.path.splitext(os.path.basename(csv_file))[0]}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Converted {len(enhanced_data)} records to {output_file}")
        print(f"📊 Success rate: {dataset['metadata']['success_rate']:.1%}")
        print(f"🎯 Quality score: {dataset['metadata']['quality_score']:.3f}")
        
        return output_file

    def _process_row(self, row, mappings: dict) -> dict:
        """Process a single CSV row into enhanced format"""
        
        processed = {
            'id': f"csv_row_{hash(str(row.to_dict()))}",
            'data_source': 'user_csv'
        }
        
        # Extract symptoms
        symptoms_col = mappings.get('symptoms')
        if symptoms_col and symptoms_col in row and pd.notna(row[symptoms_col]):
            symptoms_text = str(row[symptoms_col]).strip()
            processed['symptoms_english'] = [symptoms_text]
            processed['symptoms'] = symptoms_text
        
        # Extract diagnosis
        diagnosis_col = mappings.get('diagnosis')
        if diagnosis_col and diagnosis_col in row and pd.notna(row[diagnosis_col]):
            diagnosis = str(row[diagnosis_col]).strip()
            processed['primary_diagnosis'] = self._normalize_diagnosis(diagnosis)
            processed['diagnosis'] = diagnosis
        
        # Extract severity
        severity_col = mappings.get('severity')
        if severity_col and severity_col in row and pd.notna(row[severity_col]):
            severity = str(row[severity_col]).strip()
            processed['severity'] = self._normalize_severity(severity)
        else:
            processed['severity'] = 'medium'  # Default
        
        # Extract demographics
        demographics = {}
        
        age_col = mappings.get('age')
        if age_col and age_col in row and pd.notna(row[age_col]):
            try:
                demographics['age'] = int(float(row[age_col]))
            except (ValueError, TypeError):
                pass
        
        gender_col = mappings.get('gender')
        if gender_col and gender_col in row and pd.notna(row[gender_col]):
            gender = str(row[gender_col]).strip().lower()
            demographics['gender'] = self._normalize_gender(gender)
        
        if demographics:
            processed['patient_demographics'] = demographics
        
        # Extract duration if available
        duration_col = mappings.get('duration')
        if duration_col and duration_col in row and pd.notna(row[duration_col]):
            processed['duration'] = str(row[duration_col]).strip()
        
        # Set confidence and emergency status
        processed['confidence_score'] = 0.8  # Default confidence for CSV data
        processed['is_emergency'] = processed.get('severity') in ['high', 'critical']
        processed['created_at'] = datetime.now().isoformat()
        
        return processed

    def _normalize_diagnosis(self, diagnosis: str) -> str:
        """Normalize diagnosis names"""
        
        diagnosis = diagnosis.lower().strip()
        
        # Common diagnosis mappings
        diagnosis_mappings = {
            'flu': 'respiratory_infection',
            'influenza': 'respiratory_infection',
            'cold': 'respiratory_infection',
            'common cold': 'respiratory_infection',
            'pneumonia': 'pneumonia',
            'bronchitis': 'bronchitis',
            'asthma': 'asthma',
            'malaria': 'malaria',
            'typhoid': 'typhoid',
            'tuberculosis': 'tuberculosis',
            'tb': 'tuberculosis',
            'diabetes': 'diabetes',
            'hypertension': 'hypertension',
            'high blood pressure': 'hypertension',
            'migraine': 'migraine',
            'headache': 'tension_headache',
            'gastritis': 'gastritis',
            'food poisoning': 'food_poisoning'
        }
        
        return diagnosis_mappings.get(diagnosis, diagnosis.replace(' ', '_'))

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity values"""
        
        severity_str = str(severity).lower().strip()
        return self.severity_mappings.get(severity_str, 'medium')

    def _normalize_gender(self, gender: str) -> str:
        """Normalize gender values"""
        
        gender = gender.lower().strip()
        
        if gender in ['m', 'male', 'man']:
            return 'male'
        elif gender in ['f', 'female', 'woman']:
            return 'female'
        else:
            return 'other'

    def _identify_issues(self, df, mappings: dict) -> list:
        """Identify potential data quality issues"""
        
        issues = []
        
        # Check for required columns
        if 'symptoms' not in mappings:
            issues.append("❌ No symptoms column identified")
        
        if 'diagnosis' not in mappings:
            issues.append("❌ No diagnosis column identified")
        
        # Check for missing data
        for field, col in mappings.items():
            if col in df.columns:
                missing_pct = df[col].isnull().sum() / len(df) * 100
                if missing_pct > 10:
                    issues.append(f"⚠️ {field} column has {missing_pct:.1f}% missing data")
        
        # Check data types
        if 'symptoms' in mappings:
            symptoms_col = mappings['symptoms']
            if symptoms_col in df.columns:
                if df[symptoms_col].dtype != 'object':
                    issues.append(f"⚠️ Symptoms column should be text, found {df[symptoms_col].dtype}")
        
        return issues

    def _calculate_quality_score(self, data: list) -> float:
        """Calculate quality score for the converted dataset"""
        
        if not data:
            return 0.0
        
        # Count complete records
        complete_records = sum(1 for record in data 
                             if record.get('symptoms') and record.get('diagnosis'))
        
        # Count records with demographics
        demo_records = sum(1 for record in data 
                          if record.get('patient_demographics'))
        
        # Count records with severity
        severity_records = sum(1 for record in data 
                              if record.get('severity') != 'medium')
        
        quality_score = (
            (complete_records / len(data)) * 0.5 +  # Completeness
            (demo_records / len(data)) * 0.3 +      # Demographics
            (severity_records / len(data)) * 0.2    # Severity info
        )
        
        return quality_score

def main():
    """Main function for command-line interface"""
    
    parser = argparse.ArgumentParser(
        description='Load your CSV dataset into AI Healthcare Platform'
    )
    parser.add_argument(
        '--csv-file',
        required=True,
        help='Path to your CSV dataset file'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview how the data will be processed'
    )
    parser.add_argument(
        '--load',
        action='store_true',
        help='Convert and load the dataset'
    )
    parser.add_argument(
        '--output',
        help='Output file name for converted dataset'
    )
    parser.add_argument(
        '--mapping',
        help='JSON file with custom column mappings'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    loader = CSVDatasetLoader()
    
    # Load custom mappings if provided
    custom_mappings = None
    if args.mapping and os.path.exists(args.mapping):
        with open(args.mapping, 'r') as f:
            custom_mappings = json.load(f)
    
    # Analyze the CSV structure
    print("🔍 Analyzing your CSV file...")
    analysis = loader.analyze_csv(args.csv_file)
    
    if not analysis:
        print("❌ Failed to analyze CSV file")
        sys.exit(1)
    
    print(f"\n📊 CSV Analysis Results:")
    print(f"   Total rows: {analysis['total_rows']:,}")
    print(f"   Total columns: {analysis['total_columns']}")
    print(f"   Columns: {', '.join(analysis['columns'])}")
    
    print(f"\n🎯 Suggested Column Mappings:")
    for field, column in analysis['suggested_mappings'].items():
        print(f"   {field}: {column}")
    
    if args.preview:
        print("\n👀 Previewing data processing...")
        preview = loader.preview_data(args.csv_file, custom_mappings)
        
        if preview['issues_found']:
            print(f"\n⚠️ Issues Found:")
            for issue in preview['issues_found']:
                print(f"   {issue}")
    
    if args.load:
        print("\n🚀 Converting CSV to enhanced dataset format...")
        output_file = loader.convert_to_enhanced_format(
            args.csv_file, args.output, custom_mappings
        )
        
        if output_file:
            print(f"\n🎉 Conversion completed successfully!")
            print(f"\n📁 Next Steps:")
            print(f"1. Load into Django database:")
            print(f"   python manage.py load_enhanced_dataset --dataset-file {output_file} --create-patients")
            print(f"2. Retrain your ML model:")
            print(f"   python manage.py train_symptom_model --force-retrain --min-samples 50")
            print(f"3. Evaluate performance:")
            print(f"   python manage.py evaluate_models --compare-baseline")
        else:
            print("❌ Conversion failed")
            sys.exit(1)

if __name__ == '__main__':
    main()
