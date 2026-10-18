#!/usr/bin/env python3
from backend.ai_services import SymptomAnalyzer

def test_symptom_analyzer():
    analyzer = SymptomAnalyzer()
    
    test_cases = [
        'fever and headache',
        'persistent cough',
        'back pain and stiffness', 
        'nausea and vomiting',
        'chest pain and difficulty breathing'
    ]
    
    print('🧪 Testing Your Improved Symptom Analyzer:')
    print('=' * 50)
    
    for symptoms in test_cases:
        severity, confidence, is_emergency, predictions = analyzer.analyze_symptom(symptoms)
        primary = predictions.get('primary_diagnosis', 'unknown')
        method = predictions.get('method', 'unknown')
        
        print(f'Symptoms: "{symptoms}"')
        print(f'  → Diagnosis: {primary}')
        print(f'  → Severity: {severity}')
        print(f'  → Confidence: {confidence:.1%}')
        print(f'  → Emergency: {"Yes" if is_emergency else "No"}')
        print(f'  → Method: {method}')
        print('-' * 30)

if __name__ == '__main__':
    test_symptom_analyzer()
