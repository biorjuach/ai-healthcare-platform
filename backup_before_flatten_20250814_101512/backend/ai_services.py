from typing import Dict, List, Tuple, Optional
import numpy as np
import json
import re
import pickle
import os
from datetime import datetime, timedelta
from .models import Symptom, Diagnosis, Doctor, Patient

class SymptomAnalyzer:
    def __init__(self):
        # Enhanced symptom-disease mapping with confidence scores
        self.symptom_disease_mapping = {
            'fever': {
                'diseases': ['viral_infection', 'bacterial_infection', 'malaria', 'typhoid'],
                'weights': [0.3, 0.4, 0.2, 0.1],
                'severity': 0.7
            },
            'cough': {
                'diseases': ['respiratory_infection', 'bronchitis', 'pneumonia', 'tuberculosis'],
                'weights': [0.4, 0.3, 0.2, 0.1],
                'severity': 0.6
            },
            'headache': {
                'diseases': ['tension_headache', 'migraine', 'hypertension', 'meningitis'],
                'weights': [0.5, 0.3, 0.15, 0.05],
                'severity': 0.5
            },
            'chest_pain': {
                'diseases': ['angina', 'heart_attack', 'pneumonia', 'anxiety'],
                'weights': [0.3, 0.4, 0.2, 0.1],
                'severity': 0.9
            },
            'shortness_of_breath': {
                'diseases': ['asthma', 'pneumonia', 'heart_failure', 'anxiety'],
                'weights': [0.3, 0.3, 0.3, 0.1],
                'severity': 0.8
            },
            'abdominal_pain': {
                'diseases': ['gastritis', 'appendicitis', 'food_poisoning', 'ulcer'],
                'weights': [0.4, 0.2, 0.3, 0.1],
                'severity': 0.7
            },
            'nausea': {
                'diseases': ['food_poisoning', 'gastritis', 'pregnancy', 'migraine'],
                'weights': [0.3, 0.3, 0.2, 0.2],
                'severity': 0.5
            },
            'vomiting': {
                'diseases': ['food_poisoning', 'gastritis', 'pregnancy', 'migraine'],
                'weights': [0.4, 0.2, 0.2, 0.2],
                'severity': 0.6
            },
            'diarrhea': {
                'diseases': ['food_poisoning', 'viral_infection', 'parasitic_infection', 'ibd'],
                'weights': [0.4, 0.3, 0.2, 0.1],
                'severity': 0.6
            },
            'fatigue': {
                'diseases': ['anemia', 'viral_infection', 'depression', 'diabetes'],
                'weights': [0.3, 0.3, 0.2, 0.2],
                'severity': 0.4
            }
        }
        
        # Emergency keywords with severity levels
        self.emergency_keywords = {
            'critical': ['unconscious', 'seizure', 'severe bleeding', 'chest pain', 'difficulty breathing'],
            'high': ['high fever', 'severe pain', 'vomiting blood', 'head injury'],
            'medium': ['moderate pain', 'persistent cough', 'fever'],
            'low': ['mild pain', 'fatigue', 'mild cough']
        }
        
        # Multi-language symptom mapping (English to local languages)
        self.language_mappings = {
            'swahili': {
                'fever': ['homa', 'joto'],
                'cough': ['kikohozi', 'kukohoa'],
                'headache': ['kichwa', 'maumivu ya kichwa'],
                'chest_pain': ['maumivu ya kifua', 'kifua'],
                'abdominal_pain': ['tumbo', 'maumivu ya tumbo'],
                'nausea': ['kichefuchefu', 'kutapika'],
                'vomiting': ['kutapika', 'kupiga chura'],
                'diarrhea': ['kuhara', 'kupungua'],
                'fatigue': ['uchovu', 'kuchoka']
            }
        }
        
        # Load ML model if available
        self.ml_model = None
        self.ml_model_metadata = None
        self._load_ml_model()

    def _load_ml_model(self):
        """Load the trained ML model if available"""
        model_path = 'models/symptom_classifier.pkl'
        metadata_path = 'models/symptom_classifier_metadata.json'
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.ml_model_metadata = json.load(f)
                
                print(f"ML model loaded successfully. Trained on {self.ml_model_metadata.get('training_samples', 'unknown')} samples.")
            else:
                print("No ML model found. Using rule-based analysis only.")
        except Exception as e:
            print(f"Error loading ML model: {e}. Using rule-based analysis only.")

    def analyze_symptom(self, symptom_text: str, language: str = 'english') -> Tuple[str, float, bool, Dict]:
        """
        Enhanced symptom analysis with ML model integration and multi-language support
        """
        # Normalize and detect language
        symptom_text = symptom_text.lower().strip()
        detected_language = self._detect_language(symptom_text)
        
        # Translate to English if needed
        if detected_language != 'english':
            symptom_text = self._translate_to_english(symptom_text, detected_language)
        
        # Analyze severity and emergency status
        severity, is_emergency = self._analyze_severity(symptom_text)
        
        # Get predictions from both rule-based and ML models
        rule_based_predictions = self._predict_diseases_rule_based(symptom_text)
        ml_predictions = self._predict_diseases_ml(symptom_text)
        
        # Combine predictions
        combined_predictions = self._combine_predictions(rule_based_predictions, ml_predictions)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(symptom_text, combined_predictions)
        
        return severity, confidence_score, is_emergency, combined_predictions

    def _predict_diseases_rule_based(self, symptom_text: str) -> Dict:
        """Predict diseases using rule-based approach"""
        disease_scores = {}
        
        for symptom, mapping in self.symptom_disease_mapping.items():
            if symptom in symptom_text or symptom.replace('_', ' ') in symptom_text:
                for disease, weight in zip(mapping['diseases'], mapping['weights']):
                    if disease in disease_scores:
                        disease_scores[disease] += weight
                    else:
                        disease_scores[disease] = weight
        
        # Normalize scores and get top predictions
        if disease_scores:
            max_score = max(disease_scores.values())
            normalized_scores = {disease: score/max_score for disease, score in disease_scores.items()}
            
            # Get top 3 predictions
            top_predictions = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'predictions': top_predictions,
                'primary_diagnosis': top_predictions[0][0] if top_predictions else 'general_consultation',
                'confidence': top_predictions[0][1] if top_predictions else 0.0,
                'method': 'rule_based'
            }
        
        return {
            'predictions': [],
            'primary_diagnosis': 'general_consultation',
            'confidence': 0.0,
            'method': 'rule_based'
        }

    def _predict_diseases_ml(self, symptom_text: str) -> Dict:
        """Predict diseases using ML model"""
        if self.ml_model is None:
            return {
                'predictions': [],
                'primary_diagnosis': 'general_consultation',
                'confidence': 0.0,
                'method': 'ml_unavailable'
            }
        
        try:
            # Make prediction
            prediction = self.ml_model.predict([symptom_text])[0]
            prediction_proba = self.ml_model.predict_proba([symptom_text])[0]
            
            # Get confidence score
            confidence = np.max(prediction_proba)
            
            # Get top predictions
            classes = self.ml_model.classes_ if hasattr(self.ml_model, 'classes_') else []
            if hasattr(self.ml_model, 'named_steps') and 'classifier' in self.ml_model.named_steps:
                classes = self.ml_model.named_steps['classifier'].classes_
            
            if len(classes) > 0:
                # Get top 3 predictions
                top_indices = np.argsort(prediction_proba)[-3:][::-1]
                top_predictions = [(classes[i], prediction_proba[i]) for i in top_indices]
                
                return {
                    'predictions': top_predictions,
                    'primary_diagnosis': prediction,
                    'confidence': confidence,
                    'method': 'ml_model'
                }
            else:
                return {
                    'predictions': [(prediction, confidence)],
                    'primary_diagnosis': prediction,
                    'confidence': confidence,
                    'method': 'ml_model'
                }
                
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return {
                'predictions': [],
                'primary_diagnosis': 'general_consultation',
                'confidence': 0.0,
                'method': 'ml_error'
            }

    def _combine_predictions(self, rule_based: Dict, ml: Dict) -> Dict:
        """Combine predictions from rule-based and ML models"""
        # If ML model is not available or has low confidence, use rule-based
        if ml['method'] in ['ml_unavailable', 'ml_error'] or ml['confidence'] < 0.3:
            return rule_based
        
        # If rule-based has very low confidence, use ML
        if rule_based['confidence'] < 0.2:
            return ml
        
        # Combine predictions with weighted average
        rule_weight = 0.3
        ml_weight = 0.7
        
        # Combine primary diagnoses
        if rule_based['primary_diagnosis'] == ml['primary_diagnosis']:
            # Same diagnosis - use weighted confidence
            combined_confidence = (rule_based['confidence'] * rule_weight + 
                                 ml['confidence'] * ml_weight)
            primary_diagnosis = rule_based['primary_diagnosis']
        else:
            # Different diagnoses - use the one with higher confidence
            if ml['confidence'] > rule_based['confidence']:
                primary_diagnosis = ml['primary_diagnosis']
                combined_confidence = ml['confidence']
            else:
                primary_diagnosis = rule_based['primary_diagnosis']
                combined_confidence = rule_based['confidence']
        
        # Combine top predictions
        combined_predictions = []
        
        # Add ML predictions with higher weight
        for diagnosis, confidence in ml['predictions']:
            combined_predictions.append((diagnosis, confidence * ml_weight))
        
        # Add rule-based predictions
        for diagnosis, confidence in rule_based['predictions']:
            # Check if diagnosis already exists
            existing = [p for p in combined_predictions if p[0] == diagnosis]
            if existing:
                # Update confidence
                idx = combined_predictions.index(existing[0])
                combined_predictions[idx] = (diagnosis, existing[0][1] + confidence * rule_weight)
            else:
                combined_predictions.append((diagnosis, confidence * rule_weight))
        
        # Sort by confidence and get top 3
        combined_predictions.sort(key=lambda x: x[1], reverse=True)
        combined_predictions = combined_predictions[:3]
        
        return {
            'predictions': combined_predictions,
            'primary_diagnosis': primary_diagnosis,
            'confidence': combined_confidence,
            'method': 'combined',
            'rule_based_confidence': rule_based['confidence'],
            'ml_confidence': ml['confidence']
        }

    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on common words
        """
        swahili_words = ['homa', 'kikohozi', 'kichwa', 'tumbo', 'kutapika', 'kuhara', 'uchovu']
        if any(word in text for word in swahili_words):
            return 'swahili'
        return 'english'

    def _translate_to_english(self, text: str, source_language: str) -> str:
        """
        Translate symptoms to English for processing
        """
        if source_language == 'swahili':
            for english_symptom, swahili_variants in self.language_mappings['swahili'].items():
                for swahili_word in swahili_variants:
                    if swahili_word in text:
                        text = text.replace(swahili_word, english_symptom)
        return text

    def _analyze_severity(self, symptom_text: str) -> Tuple[str, bool]:
        """
        Analyze symptom severity and emergency status
        """
        severity = 'low'
        is_emergency = False
        
        # Check for emergency keywords
        for level, keywords in self.emergency_keywords.items():
            if any(keyword in symptom_text for keyword in keywords):
                severity = level
                if level in ['critical', 'high']:
                    is_emergency = True
                break
        
        return severity, is_emergency

    def _calculate_confidence(self, symptom_text: str, disease_predictions: Dict) -> float:
        """
        Calculate confidence score based on symptom clarity and prediction strength
        """
        base_confidence = disease_predictions.get('confidence', 0.0)
        
        # Adjust confidence based on symptom clarity
        symptom_clarity = self._assess_symptom_clarity(symptom_text)
        
        # Adjust confidence based on prediction method
        method = disease_predictions.get('method', 'rule_based')
        if method == 'combined':
            # Use the higher confidence from combined methods
            rule_confidence = disease_predictions.get('rule_based_confidence', 0.0)
            ml_confidence = disease_predictions.get('ml_confidence', 0.0)
            base_confidence = max(rule_confidence, ml_confidence)
        elif method == 'ml_model':
            # ML models tend to be more confident
            base_confidence *= 1.1
        
        # Combine base confidence with symptom clarity
        final_confidence = (base_confidence * 0.7) + (symptom_clarity * 0.3)
        
        return min(final_confidence, 1.0)

    def _assess_symptom_clarity(self, symptom_text: str) -> float:
        """
        Assess how clear and specific the symptom description is
        """
        clarity_score = 0.5  # Base score
        
        # Check for specific medical terms
        medical_terms = ['fever', 'cough', 'headache', 'pain', 'nausea', 'vomiting', 'diarrhea']
        if any(term in symptom_text for term in medical_terms):
            clarity_score += 0.2
        
        # Check for severity indicators
        severity_words = ['severe', 'mild', 'moderate', 'intense', 'sharp', 'dull']
        if any(word in symptom_text for word in severity_words):
            clarity_score += 0.1
        
        # Check for duration indicators
        duration_words = ['days', 'weeks', 'hours', 'sudden', 'gradual']
        if any(word in symptom_text for word in duration_words):
            clarity_score += 0.1
        
        # Check for location specificity
        location_words = ['chest', 'head', 'stomach', 'back', 'throat']
        if any(word in symptom_text for word in location_words):
            clarity_score += 0.1
        
        return min(clarity_score, 1.0)

    def generate_preliminary_diagnosis(self, symptom: Symptom) -> str:
        """
        Generate preliminary diagnosis text
        """
        severity, confidence, is_emergency, disease_predictions = self.analyze_symptom(symptom.description)
        
        primary_diagnosis = disease_predictions.get('primary_diagnosis', 'general_consultation')
        confidence_score = disease_predictions.get('confidence', 0.0)
        method = disease_predictions.get('method', 'rule_based')
        
        # Generate diagnosis text
        if is_emergency:
            diagnosis_text = f"EMERGENCY: {primary_diagnosis.replace('_', ' ').title()}"
        else:
            diagnosis_text = f"Preliminary diagnosis: {primary_diagnosis.replace('_', ' ').title()}"
        
        # Add confidence information
        if method == 'combined':
            diagnosis_text += f" (Confidence: {confidence_score:.1%}, Method: AI+ML)"
        elif method == 'ml_model':
            diagnosis_text += f" (Confidence: {confidence_score:.1%}, Method: ML)"
        else:
            diagnosis_text += f" (Confidence: {confidence_score:.1%}, Method: Rule-based)"
        
        return diagnosis_text

class DoctorMatcher:
    def __init__(self):
        # Enhanced specialization mapping with multiple keywords
        self.specialization_keywords = {
            'cardiologist': ['heart', 'chest pain', 'angina', 'heart attack', 'cardiac', 'blood pressure'],
            'neurologist': ['brain', 'nerve', 'seizure', 'headache', 'migraine', 'stroke', 'consciousness'],
            'pediatrician': ['child', 'baby', 'infant', 'toddler', 'teenager', 'growth'],
            'dermatologist': ['skin', 'rash', 'acne', 'eczema', 'psoriasis', 'mole'],
            'psychiatrist': ['mental', 'anxiety', 'depression', 'mood', 'behavior', 'stress'],
            'surgeon': ['surgery', 'appendicitis', 'hernia', 'trauma', 'injury'],
            'gynecologist': ['pregnancy', 'menstrual', 'vaginal', 'breast', 'fertility'],
            'ophthalmologist': ['eye', 'vision', 'blind', 'glasses', 'retina'],
            'orthopedist': ['bone', 'joint', 'fracture', 'arthritis', 'back pain'],
            'pulmonologist': ['lung', 'breathing', 'asthma', 'pneumonia', 'tuberculosis']
        }
        
        # Emergency specializations
        self.emergency_specializations = ['general', 'surgeon', 'cardiologist', 'neurologist']

    def find_appropriate_doctor(self, symptom: Symptom, patient: Patient = None) -> Optional[Doctor]:
        """
        Find the most appropriate doctor based on symptoms and patient context
        """
        symptom_text = symptom.description.lower()
        
        # Determine required specialization
        required_specialization = self._determine_specialization(symptom_text)
        
        # Get available doctors with the required specialization
        available_doctors = Doctor.objects.filter(
            specialization=required_specialization,
            is_available=True
        )
        
        if not available_doctors.exists():
            # Fallback to general practitioners
            available_doctors = Doctor.objects.filter(
                specialization='general',
                is_available=True
            )
        
        if not available_doctors.exists():
            return None
        
        # Score doctors based on experience and availability
        best_doctor = None
        best_score = 0
        
        for doctor in available_doctors:
            score = self._calculate_doctor_score(doctor, symptom, patient)
            if score > best_score:
                best_score = score
                best_doctor = doctor
        
        return best_doctor

    def _determine_specialization(self, symptom_text: str) -> str:
        """
        Determine the most appropriate specialization based on symptoms
        """
        specialization_scores = {}
        
        for specialization, keywords in self.specialization_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in symptom_text:
                    score += 1
            if score > 0:
                specialization_scores[specialization] = score
        
        if specialization_scores:
            return max(specialization_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'

    def _calculate_doctor_score(self, doctor: Doctor, symptom: Symptom, patient: Patient = None) -> float:
        """
        Calculate a score for doctor suitability
        """
        score = 0.0
        
        # Experience bonus
        score += min(doctor.years_of_experience * 0.1, 1.0)
        
        # Availability bonus
        if doctor.is_available:
            score += 0.5
        
        # Emergency specialization bonus for critical cases
        if symptom.severity in ['critical', 'high'] and doctor.specialization in self.emergency_specializations:
            score += 0.3
        
        # Location-based scoring (if patient location is available)
        if patient and patient.location:
            # This would be enhanced with actual distance calculation
            score += 0.2
        
        return score

class EmergencyResponseSystem:
    def __init__(self):
        self.critical_symptoms = [
            'unconscious', 'seizure', 'severe bleeding', 'chest pain', 
            'difficulty breathing', 'heart attack', 'stroke'
        ]
        
        self.emergency_protocols = {
            'chest_pain': {
                'immediate_action': 'Call emergency services immediately. Do not delay.',
                'priority': 'critical',
                'response_time': 5,  # minutes
                'required_specialist': 'cardiologist'
            },
            'difficulty_breathing': {
                'immediate_action': 'Seek immediate medical attention. Call emergency services.',
                'priority': 'critical',
                'response_time': 5,
                'required_specialist': 'pulmonologist'
            },
            'seizure': {
                'immediate_action': 'Call emergency services. Protect from injury.',
                'priority': 'critical',
                'response_time': 5,
                'required_specialist': 'neurologist'
            },
            'severe_bleeding': {
                'immediate_action': 'Apply direct pressure. Call emergency services.',
                'priority': 'critical',
                'response_time': 5,
                'required_specialist': 'surgeon'
            },
            'unconscious': {
                'immediate_action': 'Call emergency services immediately. Check breathing.',
                'priority': 'critical',
                'response_time': 3,
                'required_specialist': 'general'
            }
        }

    def check_emergency(self, symptom: Symptom) -> bool:
        """
        Check if symptom requires emergency response
        """
        symptom_text = symptom.description.lower()
        
        # Check for critical keywords
        for critical_symptom in self.critical_symptoms:
            if critical_symptom in symptom_text:
                return True
        
        # Check severity level
        if symptom.severity in ['critical', 'high']:
            return True
        
        return False

    def get_emergency_response_plan(self, symptom: Symptom) -> Dict:
        """
        Get comprehensive emergency response plan
        """
        symptom_text = symptom.description.lower()
        
        # Find matching emergency protocol
        for emergency_type, protocol in self.emergency_protocols.items():
            if emergency_type.replace('_', ' ') in symptom_text:
                return {
                    'emergency_type': emergency_type,
                    'immediate_action': protocol['immediate_action'],
                    'priority': protocol['priority'],
                    'response_time': protocol['response_time'],
                    'required_specialist': protocol['required_specialist'],
                    'location': symptom.patient.location if symptom.patient.location else 'Unknown',
                    'patient_phone': symptom.patient.phone_number,
                    'emergency_contacts': symptom.patient.emergency_contacts
                }
        
        # Default emergency protocol
        return {
            'emergency_type': 'general_emergency',
            'immediate_action': 'Seek immediate medical attention. Call emergency services.',
            'priority': 'high',
            'response_time': 10,
            'required_specialist': 'general',
            'location': symptom.patient.location if symptom.patient.location else 'Unknown',
            'patient_phone': symptom.patient.phone_number,
            'emergency_contacts': symptom.patient.emergency_contacts
        }

class HealthRiskAssessor:
    def __init__(self):
        self.risk_factors = {
            'age': {
                'high_risk': {'min': 65, 'max': 120},
                'medium_risk': {'min': 45, 'max': 64}
            },
            'preexisting_conditions': [
                'diabetes', 'hypertension', 'heart_disease', 'asthma', 
                'cancer', 'hiv', 'tuberculosis'
            ],
            'pregnancy_risk': ['pregnancy', 'pregnant', 'gestation']
        }

    def assess_health_risk(self, patient: Patient, symptom: Symptom) -> Dict:
        """
        Assess overall health risk based on patient profile and symptoms
        """
        risk_score = 0.0
        risk_factors = []
        
        # Age-based risk
        if patient.date_of_birth:
            age = (datetime.now().date() - patient.date_of_birth).days // 365
            if age >= 65:
                risk_score += 0.3
                risk_factors.append('elderly_age')
            elif age >= 45:
                risk_score += 0.15
                risk_factors.append('middle_age')
        
        # Pre-existing conditions
        if patient.medical_history:
            medical_history_lower = patient.medical_history.lower()
            for condition in self.risk_factors['preexisting_conditions']:
                if condition in medical_history_lower:
                    risk_score += 0.2
                    risk_factors.append(condition)
        
        # Pregnancy risk
        if patient.gender == 'female':
            symptom_text = symptom.description.lower()
            for pregnancy_term in self.risk_factors['pregnancy_risk']:
                if pregnancy_term in symptom_text:
                    risk_score += 0.25
                    risk_factors.append('pregnancy')
                    break
        
        # Symptom severity risk
        severity_risk = {
            'critical': 0.4,
            'high': 0.3,
            'medium': 0.15,
            'low': 0.05
        }
        risk_score += severity_risk.get(symptom.severity, 0.1)
        
        # Determine risk level
        if risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self._get_risk_recommendations(risk_level, risk_factors)
        }

    def _get_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """
        Get recommendations based on risk level and factors
        """
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                'Immediate medical attention recommended',
                'Consider emergency consultation',
                'Monitor symptoms closely'
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                'Schedule appointment within 24-48 hours',
                'Monitor symptoms for worsening',
                'Consider telemedicine consultation'
            ])
        else:
            recommendations.extend([
                'Schedule routine appointment',
                'Monitor symptoms',
                'Follow up if symptoms persist'
            ])
        
        # Specific recommendations based on risk factors
        if 'pregnancy' in risk_factors:
            recommendations.append('Consult obstetrician/gynecologist')
        if 'elderly_age' in risk_factors:
            recommendations.append('Consider geriatric consultation')
        if 'diabetes' in risk_factors:
            recommendations.append('Monitor blood sugar levels')
        
        return recommendations 