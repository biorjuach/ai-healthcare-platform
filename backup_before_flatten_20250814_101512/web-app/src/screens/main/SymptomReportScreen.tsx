import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  ArrowRight, 
  Activity, 
  MapPin, 
  Clock, 
  AlertTriangle,
  Brain,
  CheckCircle,
  Phone
} from 'lucide-react';
import toast from 'react-hot-toast';
import apiService from '../../services/api';

interface SymptomFormData {
  symptoms: string;
  body_location: string;
  duration: string;
  severity: string;
  description: string;
  language: 'en' | 'sw';
}

const SymptomReportScreen: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [locationData, setLocationData] = useState<any>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid },
  } = useForm<SymptomFormData>({
    mode: 'onChange',
    defaultValues: {
      language: 'en',
    },
  });

  const watchedValues = watch();

  // Get current location
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocationData({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            address: 'Current Location',
          });
          toast.success('Location captured successfully');
        },
        (error) => {
          toast.error('Unable to get location. Please enter manually.');
        }
      );
    } else {
      toast.error('Geolocation is not supported by this browser.');
    }
  };

  // Analyze symptoms mutation
  const analyzeMutation = useMutation(
    (data: SymptomFormData) => apiService.analyzeSymptoms({
      ...data,
      location_data: locationData,
    }),
    {
      onSuccess: (data) => {
        setAnalysisResult(data);
        setIsAnalyzing(false);
        setCurrentStep(4);
      },
      onError: (error) => {
        setIsAnalyzing(false);
        toast.error('Failed to analyze symptoms. Please try again.');
      },
    }
  );

  // Submit symptom report mutation
  const submitMutation = useMutation(
    (data: SymptomFormData) => apiService.submitSymptomReport({
      ...data,
      location_data: locationData,
    }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('patientSymptoms');
        queryClient.invalidateQueries('patientDashboard');
        toast.success('Symptom report submitted successfully');
        navigate('/symptoms');
      },
      onError: () => {
        toast.error('Failed to submit symptom report');
      },
    }
  );

  const handleAnalyze = async (data: SymptomFormData) => {
    setIsAnalyzing(true);
    analyzeMutation.mutate(data);
  };

  const handleSubmitReport = async (data: SymptomFormData) => {
    submitMutation.mutate(data);
  };

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-danger-600 bg-danger-50 border-danger-200';
      case 'high': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'medium': return 'text-primary-600 bg-primary-50 border-primary-200';
      case 'low': return 'text-secondary-600 bg-secondary-50 border-secondary-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const handleEmergencyCall = () => {
    if (analysisResult?.analysis_result?.emergency_detected) {
      window.open('tel:911', '_self');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Report Symptoms</h1>
          <p className="text-gray-600">Get AI-powered analysis of your symptoms</p>
        </div>
        <button
          onClick={() => navigate('/symptoms')}
          className="btn-secondary flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Symptoms
        </button>
      </div>

      {/* Progress Steps */}
      <div className="card">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= step 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {step}
              </div>
              {step < 4 && (
                <div className={`w-16 h-1 mx-2 ${
                  currentStep > step ? 'bg-primary-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>Symptoms</span>
          <span>Location</span>
          <span>Details</span>
          <span>Analysis</span>
        </div>
      </div>

      <form onSubmit={handleSubmit(handleAnalyze)}>
        {/* Step 1: Symptoms */}
        {currentStep === 1 && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Activity className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">Describe Your Symptoms</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What symptoms are you experiencing?
                </label>
                <textarea
                  {...register('symptoms', { required: 'Please describe your symptoms' })}
                  rows={4}
                  className="input-field"
                  placeholder="e.g., headache, fever, chest pain, nausea..."
                />
                {errors.symptoms && (
                  <p className="mt-1 text-sm text-danger-600">{errors.symptoms.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language Preference
                </label>
                <select {...register('language')} className="input-field">
                  <option value="en">English</option>
                  <option value="sw">Swahili</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                type="button"
                onClick={nextStep}
                disabled={!watchedValues.symptoms}
                className="btn-primary"
              >
                Next
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Body Location */}
        {currentStep === 2 && (
          <div className="card">
            <div className="flex items-center mb-4">
              <MapPin className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">Body Location</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Where are you experiencing symptoms?
                </label>
                <input
                  {...register('body_location', { required: 'Please specify the body location' })}
                  type="text"
                  className="input-field"
                  placeholder="e.g., head, chest, abdomen, left arm..."
                />
                {errors.body_location && (
                  <p className="mt-1 text-sm text-danger-600">{errors.body_location.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location Services
                </label>
                <button
                  type="button"
                  onClick={getCurrentLocation}
                  className="btn-secondary w-full"
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  Get Current Location
                </button>
                {locationData && (
                  <p className="mt-2 text-sm text-secondary-600">
                    ✓ Location captured: {locationData.latitude.toFixed(4)}, {locationData.longitude.toFixed(4)}
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-between mt-6">
              <button type="button" onClick={prevStep} className="btn-secondary">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </button>
              <button
                type="button"
                onClick={nextStep}
                disabled={!watchedValues.body_location}
                className="btn-primary"
              >
                Next
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Duration and Severity */}
        {currentStep === 3 && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Clock className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">Duration and Severity</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How long have you been experiencing these symptoms?
                </label>
                <input
                  {...register('duration', { required: 'Please specify the duration' })}
                  type="text"
                  className="input-field"
                  placeholder="e.g., 2 hours, 3 days, 1 week..."
                />
                {errors.duration && (
                  <p className="mt-1 text-sm text-danger-600">{errors.duration.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How severe are your symptoms?
                </label>
                <select
                  {...register('severity', { required: 'Please select severity level' })}
                  className="input-field"
                >
                  <option value="">Select severity...</option>
                  <option value="low">Low - Mild discomfort</option>
                  <option value="medium">Medium - Noticeable but manageable</option>
                  <option value="high">High - Significant discomfort</option>
                  <option value="critical">Critical - Severe pain or emergency</option>
                </select>
                {errors.severity && (
                  <p className="mt-1 text-sm text-danger-600">{errors.severity.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Details (Optional)
                </label>
                <textarea
                  {...register('description')}
                  rows={3}
                  className="input-field"
                  placeholder="Any additional information that might help with analysis..."
                />
              </div>
            </div>

            <div className="flex justify-between mt-6">
              <button type="button" onClick={prevStep} className="btn-secondary">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </button>
              <button
                type="submit"
                disabled={isAnalyzing || !isValid}
                className="btn-primary"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    Analyze Symptoms
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Analysis Results */}
        {currentStep === 4 && analysisResult && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Brain className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">AI Analysis Results</h2>
            </div>

            {/* Emergency Alert */}
            {analysisResult.analysis_result.emergency_detected && (
              <div className="bg-danger-50 border border-danger-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <AlertTriangle className="h-6 w-6 text-danger-600 mr-2" />
                  <div>
                    <h3 className="font-semibold text-danger-900">Emergency Detected</h3>
                    <p className="text-danger-700">Your symptoms may require immediate medical attention.</p>
                  </div>
                </div>
                <button
                  onClick={handleEmergencyCall}
                  className="btn-danger mt-3 flex items-center"
                >
                  <Phone className="h-4 w-4 mr-2" />
                  Call Emergency Services
                </button>
              </div>
            )}

            {/* Analysis Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Severity Assessment</h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(analysisResult.analysis_result.severity)}`}>
                  {analysisResult.analysis_result.severity}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-2">AI Confidence</h3>
                <div className="flex items-center">
                  <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full" 
                      style={{ width: `${analysisResult.ai_confidence}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">{analysisResult.ai_confidence}%</span>
                </div>
              </div>
            </div>

            {/* Predicted Conditions */}
            {analysisResult.analysis_result.predicted_diseases?.length > 0 && (
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 mb-2">Possible Conditions</h3>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.analysis_result.predicted_diseases.map((disease: string, index: number) => (
                    <span key={index} className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full">
                      {disease}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Treatment Suggestions */}
            {analysisResult.analysis_result.treatment_suggestions?.length > 0 && (
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 mb-2">Treatment Suggestions</h3>
                <ul className="space-y-2">
                  {analysisResult.analysis_result.treatment_suggestions.map((treatment: string, index: number) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-secondary-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{treatment}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-between">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="btn-secondary"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </button>
              
              <div className="space-x-3">
                <button
                  type="button"
                  onClick={() => navigate('/symptoms')}
                  className="btn-secondary"
                >
                  Save for Later
                </button>
                <button
                  type="button"
                  onClick={() => submitMutation.mutate(watchedValues)}
                  disabled={submitMutation.isLoading}
                  className="btn-primary"
                >
                  {submitMutation.isLoading ? 'Submitting...' : 'Submit Report'}
                </button>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default SymptomReportScreen;
