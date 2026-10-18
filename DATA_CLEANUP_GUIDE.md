# Data Cleanup Guide

This guide helps you remove old symptoms and diagnoses from your database while preserving the CSV-imported data.

## Step 1: Inspect Your Data

First, run the inspection command to see what data you have:

```bash
cd backend
python manage.py inspect_data
```

This will show you:
- Total counts of symptoms and diagnoses
- Different patterns in your data
- Examples of old vs new data
- Patient distribution
- Recommendations for cleanup

## Step 2: Identify Old Data Patterns

Based on the inspection, you can identify old data using these patterns:

### Pattern 1: "(for username)" Format
Data created by `populate_symptoms_diagnoses.py` typically has:
- Symptoms: "Fever (for john_doe)"
- Diagnoses: "Common Cold (for john_doe)"

### Pattern 2: Demo/Test Patients
Data for demo patients with usernames like:
- demo_patient_1
- test_patient
- sample_user
- default

### Pattern 3: By Date
Remove data created before a specific date (e.g., before CSV import)

### Pattern 4: Specific Patients
Remove data for specific patient usernames

## Step 3: Preview Cleanup (Dry Run)

Always run a dry run first to see what would be deleted:

```bash
# Check for "(for username)" pattern (most common)
python manage.py clean_old_data --dry-run

# Check for demo patients
python manage.py clean_old_data --pattern demo_patients --dry-run

# Check for data before specific date
python manage.py clean_old_data --pattern before_date --before-date 2024-01-15 --dry-run

# Check for specific patients
python manage.py clean_old_data --pattern by_patient --patient-usernames demo_patient_1 test_user --dry-run
```

## Step 4: Perform Cleanup

Once you're satisfied with the preview, run the actual cleanup:

```bash
# Remove data with "(for username)" pattern
python manage.py clean_old_data --confirm

# Remove demo patient data
python manage.py clean_old_data --pattern demo_patients --confirm

# Remove data before specific date
python manage.py clean_old_data --pattern before_date --before-date 2024-01-15 --confirm

# Remove data for specific patients
python manage.py clean_old_data --pattern by_patient --patient-usernames demo_patient_1 test_user --confirm
```

## Step 5: Verify Results

After cleanup, run the inspection again to verify:

```bash
python manage.py inspect_data
```

## Safety Features

- **Dry Run Mode**: Always preview changes with `--dry-run`
- **Confirmation Required**: Must use `--confirm` flag for actual deletion
- **Transaction Safety**: All deletions happen in a database transaction
- **Preservation Check**: Warns if all data would be deleted
- **Detailed Logging**: Shows exactly what will be deleted

## Common Scenarios

### Scenario 1: Basic Cleanup
You ran `populate_symptoms_diagnoses.py` before importing CSV data:
```bash
python manage.py clean_old_data --dry-run
python manage.py clean_old_data --confirm
```

### Scenario 2: Multiple Demo Accounts
You have various test/demo accounts:
```bash
python manage.py clean_old_data --pattern demo_patients --dry-run
python manage.py clean_old_data --pattern demo_patients --confirm
```

### Scenario 3: Date-based Cleanup
You know the exact date when you imported CSV data:
```bash
python manage.py clean_old_data --pattern before_date --before-date 2024-01-20 --dry-run
python manage.py clean_old_data --pattern before_date --before-date 2024-01-20 --confirm
```

## Troubleshooting

### "No old data found"
- Run `python manage.py inspect_data` to see data patterns
- The old data might not match expected patterns
- Consider using date-based or patient-specific cleanup

### "Would delete all data"
- This means CSV data might not be imported yet
- Or CSV data has similar naming patterns
- Verify your CSV import was successful first

### "Permission denied" or similar errors
- Ensure you have proper database permissions
- Check database connectivity
- Run migrations if needed: `python manage.py migrate`

## Backup Recommendation

Before running any cleanup, consider backing up your database:

```bash
# For SQLite
cp db.sqlite3 db.sqlite3.backup

# For PostgreSQL
pg_dump your_database > backup.sql

# For MySQL
mysqldump your_database > backup.sql
```

This way you can restore if something goes wrong.
