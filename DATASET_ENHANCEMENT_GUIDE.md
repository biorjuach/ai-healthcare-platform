# Dataset Enhancement Guide for AI Healthcare Platform

## 🎯 Overview

This guide shows you how to significantly improve your symptom analysis system by adding a sophisticated dataset with **2000+ samples**, **regional health patterns**, and **multi-language support**.

## 🚀 Quick Start

### Step 1: Generate Enhanced Dataset

```bash
# Generate 2000 synthetic samples with East African health patterns
python enhance_dataset.py --action merge_all --samples 2000 --output enhanced_training_data.json
```

### Step 2: Load into Database

```bash
# Load the enhanced dataset into your Django database
python manage.py load_enhanced_dataset --dataset-file enhanced_training_data.json --create-patients --clear-existing
```

### Step 3: Retrain Your Model

```bash
# Retrain with the new dataset
python manage.py train_symptom_model --force-retrain --min-samples 100 --data-days 365
```

### Step 4: Evaluate Performance

```bash
# Compare the new model with baseline
python manage.py evaluate_models --compare-baseline --test-days 30
```

## 📊 What You Get

### Enhanced Dataset Features

| Feature | Before | After |
|---------|--------|-------|
| **Training Samples** | 28 | 2000+ |
| **Disease Coverage** | 7 | 20+ |
| **Languages** | English only | English + Swahili |
| **Regional Focus** | Generic | East Africa/Kenya |
| **Data Quality** | Basic | Medical-grade patterns |

### Regional Health Focus

The enhanced dataset includes:

- **Malaria** (15% prevalence) - Fever, chills, headache, nausea
- **Tuberculosis** (8% prevalence) - Persistent cough, chest pain, night sweats
- **Typhoid** (6% prevalence) - High fever, abdominal pain, diarrhea
- **Respiratory Infections** (25% prevalence) - Cough, sore throat, fever
- **Gastroenteritis** (20% prevalence) - Diarrhea, vomiting, abdominal pain
- **Hypertension** (12% prevalence) - Headache, dizziness, chest pain
- **Diabetes** (10% prevalence) - Excessive thirst, frequent urination

### Multi-Language Support

**English Symptoms:**
- "I have a severe headache and fever"
- "Persistent cough with chest pain"
- "Feeling nauseous and vomiting"

**Swahili Translations:**
- "Nina homa na kichwa kinauma"
- "Kikohozi kinachoendelea na maumivu ya kifua"
- "Nina kichefuchefu na kutapika"

## 🛠️ Implementation Steps

### 1. Data Generation Options

#### Option A: Comprehensive Dataset (Recommended)
```bash
# Create full enhanced dataset with regional patterns
python enhance_dataset.py --action merge_all --samples 2000
```

#### Option B: Synthetic Only
```bash
# Generate only synthetic regional data
python enhance_dataset.py --action create_synthetic --samples 1500
```

#### Option C: External Data Integration
```bash
# Load external medical datasets (if available)
python enhance_dataset.py --action load_external --external-data path/to/ddxplus.csv
```

### 2. Database Integration

#### Clear and Reload (Recommended for Testing)
```bash
python manage.py load_enhanced_dataset \
    --dataset-file enhanced_training_data.json \
    --clear-existing \
    --create-patients \
    --batch-size 100
```

#### Append to Existing Data
```bash
python manage.py load_enhanced_dataset \
    --dataset-file enhanced_training_data.json \
    --create-patients
```

### 3. Model Training Configuration

#### Basic Retraining
```bash
python manage.py train_symptom_model --force-retrain --min-samples 100
```

#### Advanced Training with Hyperparameter Tuning
```bash
# Edit backend/management/commands/train_symptom_model.py
# Update the _create_model method with enhanced parameters:

def _create_model(self):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=1500,      # Increased from 1000
            ngram_range=(1, 3),     # Include trigrams
            stop_words='english',
            min_df=2,
            max_df=0.9              # Reduced from 0.95
        )),
        ('classifier', RandomForestClassifier(
            n_estimators=150,       # Increased from 100
            max_depth=15,           # Increased from 10
            random_state=42,
            class_weight='balanced',
            min_samples_split=5,
            min_samples_leaf=2
        ))
    ])
    return pipeline
```

## 📈 Expected Performance Improvements

### Before Enhancement
- **Accuracy**: 65-75%
- **Training Samples**: 28
- **Disease Classes**: 7
- **Cross-validation**: High variance

### After Enhancement
- **Accuracy**: 80-90%
- **Training Samples**: 2000+
- **Disease Classes**: 20+
- **Cross-validation**: Stable performance
- **Regional Relevance**: High for East Africa

## 🔍 Quality Assurance

### Dataset Validation

The enhanced dataset includes built-in quality checks:

```python
# Quality score calculation
quality_factors = {
    'sample_size': min(total_samples / 1000, 1.0) * 0.3,
    'diagnosis_diversity': min(unique_diagnoses / 10, 1.0) * 0.3,
    'confidence_average': avg_confidence * 0.2,
    'severity_balance': severity_balance * 0.2
}
```

### Data Verification Commands

```bash
# Check data loading success
python manage.py shell -c "
from backend.models import Symptom, Diagnosis
print(f'Symptoms: {Symptom.objects.count()}')
print(f'Diagnoses: {Diagnosis.objects.count()}')
print(f'Enhanced data: {Symptom.objects.filter(input_method=\"enhanced_dataset\").count()}')
"

# Verify model performance
python manage.py evaluate_models --compare-baseline
```

## 🌍 Customization for Different Regions

### Modify Regional Patterns

Edit `enhance_dataset.py` to customize for your region:

```python
# Example: West African health patterns
self.regional_diseases = {
    'yellow_fever': {
        'symptoms': ['fever', 'headache', 'jaundice', 'muscle_pain'],
        'prevalence': 0.08,
        'severity_distribution': {'low': 0.3, 'medium': 0.4, 'high': 0.25, 'critical': 0.05}
    },
    'dengue_fever': {
        'symptoms': ['high_fever', 'severe_headache', 'eye_pain', 'muscle_joint_pain'],
        'prevalence': 0.12,
        'severity_distribution': {'low': 0.2, 'medium': 0.5, 'high': 0.25, 'critical': 0.05}
    }
    # Add more regional diseases...
}
```

### Add New Languages

```python
# Example: French translations for West Africa
self.french_translations = {
    'fever': ['fièvre', 'température élevée'],
    'headache': ['mal de tête', 'céphalée'],
    'cough': ['toux', 'tousser'],
    # Add more translations...
}
```

## 🔧 Advanced Configuration

### Continuous Learning Setup

1. **Set up automatic data collection:**
```bash
# Create cron job for weekly dataset updates
echo "0 2 * * 0 cd /path/to/project && python enhance_dataset.py --action create_synthetic --samples 100 && python manage.py load_enhanced_dataset --dataset-file enhanced_training_data.json" | crontab -
```

2. **Implement feedback loops:**
```python
# In your views.py, collect user feedback
def submit_diagnosis_feedback(request):
    feedback = {
        'symptom_id': request.POST.get('symptom_id'),
        'ai_diagnosis': request.POST.get('ai_diagnosis'),
        'actual_diagnosis': request.POST.get('actual_diagnosis'),
        'accuracy_rating': request.POST.get('rating'),
        'timestamp': timezone.now()
    }
    # Store feedback for future retraining
```

### External Dataset Integration

#### DDXPlus Dataset
```bash
# Download DDXPlus dataset
wget https://figshare.com/ndownloader/files/XXX -O ddxplus_dataset.csv

# Integrate with your dataset
python enhance_dataset.py --action load_external --external-data ddxplus_dataset.csv
```

#### Custom CSV Format
Your CSV should have columns:
- `symptoms`: Text description of symptoms
- `diagnosis`: Primary diagnosis
- `severity`: low/medium/high/critical
- `patient_age`: Age in years
- `patient_gender`: male/female/other

## 📊 Monitoring and Maintenance

### Performance Monitoring

```bash
# Weekly model evaluation
python manage.py evaluate_models --test-days 7 > reports/weekly_performance.txt

# Monthly comprehensive review
python manage.py evaluate_models --compare-baseline --test-days 30 > reports/monthly_review.txt
```

### Quality Metrics Dashboard

Track these metrics in your admin dashboard:

- **Model Accuracy**: Target >80%
- **Confidence Score**: Average >0.7
- **Emergency Detection**: Precision >90%
- **Language Coverage**: English + Swahili
- **Regional Relevance**: East African diseases well-represented

## 🚨 Troubleshooting

### Common Issues

#### "Insufficient training data"
```bash
# Solution: Lower minimum samples threshold
python manage.py train_symptom_model --min-samples 50 --force-retrain
```

#### "Low model accuracy"
```bash
# Solution: Check data quality and increase samples
python enhance_dataset.py --action merge_all --samples 3000
python manage.py load_enhanced_dataset --clear-existing --create-patients
python manage.py train_symptom_model --force-retrain
```

#### "Memory errors during training"
```bash
# Solution: Reduce feature dimensions
# Edit train_symptom_model.py:
# Change max_features from 1500 to 1000
# Change n_estimators from 150 to 100
```

### Data Quality Checks

```python
# Check for data consistency
python manage.py shell -c "
from backend.models import Symptom
symptoms = Symptom.objects.filter(input_method='enhanced_dataset')
print(f'Total enhanced symptoms: {symptoms.count()}')

# Check diagnosis distribution
from collections import Counter
diagnoses = [s.diagnosis_set.first().preliminary_diagnosis for s in symptoms if s.diagnosis_set.exists()]
diagnosis_counts = Counter(diagnoses)
print('Top diagnoses:', diagnosis_counts.most_common(10))
"
```

## 🔮 Future Enhancements

### Planned Features

1. **Deep Learning Models**: Neural networks for better text understanding
2. **Transfer Learning**: Pre-trained medical language models (BioBERT, ClinicalBERT)
3. **Real-time Learning**: Online learning from user feedback
4. **Ensemble Methods**: Combine multiple model types
5. **Symptom Severity Prediction**: AI-powered triage

### Research Integration

- **PubMed Integration**: Automatic medical literature updates
- **ICD-10 Mapping**: International disease classification
- **SNOMED CT**: Clinical terminology integration
- **Local Health Ministry**: Regional health surveillance data

## 📞 Support

### Getting Help

1. **Check the logs**: `tail -f logs/django.log`
2. **Validate data**: Use the verification commands above
3. **Test incrementally**: Start with small samples
4. **Monitor performance**: Regular evaluation runs

### Community Resources

- **Medical ML Community**: Share insights and improvements
- **Healthcare AI Forums**: Best practices and challenges
- **Regional Health Networks**: Local disease patterns

---

**🎉 Congratulations!** You now have a sophisticated, regionally-relevant dataset that will significantly improve your AI healthcare platform's diagnostic capabilities for East African populations.

**Next Steps:**
1. Generate your enhanced dataset
2. Load it into your database  
3. Retrain your models
4. Monitor performance improvements
5. Set up continuous learning workflows
