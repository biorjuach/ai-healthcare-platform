# Machine Learning Training Guide

This guide explains how to use the machine learning training system that has been added to the AI Healthcare Platform.

## 🎯 Overview

The system now includes comprehensive ML training capabilities that enable:

1. **Initial Model Training**: Train models from historical data
2. **Continuous Learning**: Retrain models using doctor feedback and patient outcomes
3. **Model Evaluation**: Assess model performance and compare with baselines
4. **Disease Mapping Updates**: Analyze patterns and update symptom-disease mappings

## 🚀 Quick Start

### 1. Initial Setup

First, ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Train Initial Model

Train the first ML model using historical data:

```bash
python manage.py train_symptom_model --data-days 365 --min-samples 50
```

### 3. Update Disease Mappings

Analyze patterns and update symptom-disease mappings:

```bash
python manage.py update_disease_mappings --data-days 365 --min-occurrences 5
```

### 4. Evaluate Model Performance

Evaluate the trained model:

```bash
python manage.py evaluate_models --compare-baseline
```

## 📊 Training Commands

### 1. `train_symptom_model`

Trains a symptom classification model using historical data.

**Usage:**
```bash
python manage.py train_symptom_model [options]
```

**Options:**
- `--data-days`: Number of days of historical data to use (default: 365)
- `--test-size`: Proportion of data for testing (default: 0.2)
- `--min-samples`: Minimum samples required (default: 50)
- `--force-retrain`: Force retraining even if model exists

**Example:**
```bash
# Train with last 6 months of data
python manage.py train_symptom_model --data-days 180 --min-samples 100

# Force retrain existing model
python manage.py train_symptom_model --force-retrain
```

**Output:**
- Model file: `models/symptom_classifier.pkl`
- Metadata: `models/symptom_classifier_metadata.json`
- Training report with accuracy metrics

### 2. `update_disease_mappings`

Analyzes historical data to update symptom-disease mappings.

**Usage:**
```bash
python manage.py update_disease_mappings [options]
```

**Options:**
- `--data-days`: Days of data to analyze (default: 365)
- `--min-occurrences`: Minimum occurrences for symptom-disease pairs (default: 5)
- `--similarity-threshold`: Threshold for clustering similar symptoms (default: 0.7)
- `--output-file`: Output file name (default: updated_disease_mappings.json)

**Example:**
```bash
# Analyze last year with higher threshold
python manage.py update_disease_mappings --data-days 365 --min-occurrences 10

# Use custom similarity threshold
python manage.py update_disease_mappings --similarity-threshold 0.8
```

**Output:**
- Updated mappings: `models/updated_disease_mappings.json`
- Statistics and analysis summary

### 3. `evaluate_models`

Evaluates model performance and generates reports.

**Usage:**
```bash
python manage.py evaluate_models [options]
```

**Options:**
- `--model-path`: Path to model file (default: models/symptom_classifier.pkl)
- `--test-days`: Days of recent data for testing (default: 30)
- `--output-dir`: Directory for reports (default: reports)
- `--compare-baseline`: Compare with rule-based baseline

**Example:**
```bash
# Evaluate with baseline comparison
python manage.py evaluate_models --compare-baseline --test-days 60

# Use custom model and output directory
python manage.py evaluate_models --model-path models/custom_model.pkl --output-dir custom_reports
```

**Output:**
- Evaluation report: `reports/model_evaluation_YYYYMMDD_HHMMSS.json`
- Detailed metrics: `reports/detailed_metrics_YYYYMMDD_HHMMSS.json`

### 4. `retrain_with_feedback`

Retrains models using doctor feedback and patient outcomes.

**Usage:**
```bash
python manage.py retrain_with_feedback [options]
```

**Options:**
- `--feedback-days`: Days of feedback data to use (default: 30)
- `--min-feedback-samples`: Minimum feedback samples required (default: 20)
- `--improvement-threshold`: Minimum accuracy improvement required (default: 0.02)
- `--backup-existing`: Backup existing model before retraining

**Example:**
```bash
# Retrain with last 2 months of feedback
python manage.py retrain_with_feedback --feedback-days 60 --min-feedback-samples 30

# Retrain with higher improvement threshold
python manage.py retrain_with_feedback --improvement-threshold 0.05 --backup-existing
```

**Output:**
- New model (if improvement threshold met)
- Backup of existing model (if requested)
- Training report with improvement metrics

## 🔄 Continuous Learning Workflow

### Automated Retraining Schedule

Set up automated retraining using cron jobs:

```bash
# Weekly retraining with feedback
0 2 * * 0 cd /path/to/project && python manage.py retrain_with_feedback --feedback-days 7 --min-feedback-samples 10

# Monthly mapping updates
0 3 1 * * cd /path/to/project && python manage.py update_disease_mappings --data-days 30

# Weekly model evaluation
0 4 * * 0 cd /path/to/project && python manage.py evaluate_models --test-days 7
```

### Feedback Collection

The system automatically collects feedback from:

1. **Doctor Confirmations**: When doctors review AI-generated diagnoses
2. **Treatment Outcomes**: Based on medical records and follow-up requirements
3. **Patient Outcomes**: Success/failure indicators from treatment notes

### Model Deployment

Models are automatically deployed when:

- Accuracy improvement exceeds threshold
- Cross-validation scores are stable
- No critical errors detected

## 📈 Model Performance Monitoring

### Key Metrics

1. **Accuracy**: Overall classification accuracy
2. **F1-Score**: Balanced precision and recall
3. **Cross-validation**: Stability across different data splits
4. **Confidence Analysis**: Relationship between confidence and accuracy
5. **Baseline Comparison**: Performance vs rule-based system

### Performance Thresholds

- **Minimum Accuracy**: 70%
- **Minimum F1-Score**: 0.65
- **Maximum CV Variance**: 0.1
- **Improvement Threshold**: 2%

### Alert Conditions

The system generates warnings for:

- Accuracy below 70%
- High cross-validation variance (>0.1)
- Model not outperforming baseline
- Insufficient training data

## 🛠️ Advanced Configuration

### Model Architecture

The ML pipeline uses:

```python
Pipeline([
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
```

### Feature Engineering

- **Text Features**: TF-IDF vectors from symptom descriptions
- **N-grams**: Unigrams and bigrams for context
- **Feature Selection**: Top 1000 most informative features
- **Stop Words**: English stop words removed

### Hyperparameter Tuning

For enhanced models (retraining):

```python
Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=1500,  # More features
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
```

## 📁 File Structure

```
models/
├── symptom_classifier.pkl              # Trained model
├── symptom_classifier_metadata.json    # Model metadata
├── updated_disease_mappings.json       # Updated mappings
└── backups/                           # Model backups
    ├── symptom_classifier_backup_20240101_120000.pkl
    └── symptom_classifier_metadata_backup_20240101_120000.json

reports/
├── model_evaluation_20240101_120000.json
├── detailed_metrics_20240101_120000.json
└── ...
```

## 🔍 Troubleshooting

### Common Issues

1. **Insufficient Training Data**
   ```
   Solution: Collect more historical data or reduce min-samples threshold
   ```

2. **Low Model Accuracy**
   ```
   Solution: 
   - Check data quality
   - Increase training data
   - Adjust hyperparameters
   - Review feature engineering
   ```

3. **High Cross-validation Variance**
   ```
   Solution:
   - Increase training data
   - Reduce model complexity
   - Check for data leakage
   ```

4. **Model Not Loading**
   ```
   Solution:
   - Check file permissions
   - Verify pickle compatibility
   - Reinstall dependencies
   ```

### Debug Commands

```bash
# Check model file integrity
python -c "import pickle; pickle.load(open('models/symptom_classifier.pkl', 'rb'))"

# Verify data availability
python manage.py shell -c "from backend.models import Symptom; print(Symptom.objects.count())"

# Test model prediction
python manage.py shell -c "from backend.ai_services import SymptomAnalyzer; analyzer = SymptomAnalyzer(); print(analyzer.analyze_symptom('I have a fever'))"
```

## 📊 Performance Benchmarks

### Expected Performance

- **Initial Model**: 65-75% accuracy
- **After Feedback Retraining**: 75-85% accuracy
- **Cross-validation**: ±5% variance
- **Baseline Comparison**: 10-20% improvement

### Success Criteria

- Model accuracy > 70%
- F1-score > 0.65
- Outperforms rule-based baseline
- Stable cross-validation scores

## 🔮 Future Enhancements

### Planned Features

1. **Deep Learning Models**: Neural networks for better text understanding
2. **Transfer Learning**: Pre-trained medical language models
3. **Ensemble Methods**: Combine multiple model types
4. **Real-time Learning**: Online learning from new data
5. **A/B Testing**: Compare different model versions

### Research Areas

- Multi-language model training
- Rare disease detection
- Symptom severity prediction
- Treatment recommendation models
- Patient outcome prediction

## 📞 Support

For issues with the ML training system:

1. Check the troubleshooting section
2. Review model logs and reports
3. Verify data quality and availability
4. Contact the development team

---

**Note**: This ML system is designed to complement, not replace, medical expertise. All AI-generated diagnoses should be reviewed by qualified healthcare professionals.
