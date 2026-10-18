import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

const SymptomsScreen: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const { data: symptoms, isLoading, error } = useQuery(
    'patientSymptoms',
    async () => {
      try {
        return await apiService.getPatientSymptoms();
      } catch (err) {
        console.error('Symptoms API error:', err);
        return []; // Return empty array as fallback
      }
    },
    {
      refetchInterval: 30000,
    }
  );

  if (isLoading) return <LoadingSpinner />;
  // Don't show error screen, just continue with empty data
  if (error) {
    console.error('Symptoms error:', error);
  }

  const filteredSymptoms = symptoms?.filter((symptom: any) => {
    const matchesSearch = symptom.symptoms.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         symptom.body_location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || symptom.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  }) || [];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-danger-600 bg-danger-50 border-danger-200';
      case 'high': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'medium': return 'text-primary-600 bg-primary-50 border-primary-200';
      case 'low': return 'text-secondary-600 bg-secondary-50 border-secondary-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="h-4 w-4" />;
      case 'high': return <AlertTriangle className="h-4 w-4" />;
      case 'medium': return <Activity className="h-4 w-4" />;
      case 'low': return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'bg-secondary-100 text-secondary-700';
      case 'active': return 'bg-warning-100 text-warning-700';
      case 'monitoring': return 'bg-primary-100 text-primary-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Symptom History</h1>
          <p className="text-gray-600">Track and manage your reported symptoms</p>
        </div>
        <Link to="/symptoms/report" className="btn-primary flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Report Symptoms
        </Link>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search symptoms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Symptoms List */}
      <div className="space-y-4">
        {filteredSymptoms.length > 0 ? (
          filteredSymptoms.map((symptom: any) => (
            <div key={symptom.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{symptom.symptoms}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(symptom.severity)}`}>
                      <div className="flex items-center space-x-1">
                        {getSeverityIcon(symptom.severity)}
                        <span>{symptom.severity}</span>
                      </div>
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Location</p>
                      <p className="text-gray-900">{symptom.body_location}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Duration</p>
                      <p className="text-gray-900">{symptom.duration}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Reported</p>
                      <p className="text-gray-900">{format(new Date(symptom.created_at), 'MMM dd, yyyy')}</p>
                    </div>
                  </div>
                  
                  {symptom.description && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-600">Description</p>
                      <p className="text-gray-900">{symptom.description}</p>
                    </div>
                  )}

                  {/* Analysis Results */}
                  {symptom.analysis && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">AI Analysis Results</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Predicted Conditions</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {symptom.analysis.predicted_diseases?.map((disease: string, index: number) => (
                              <span key={index} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded">
                                {disease}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-600">Treatment Suggestions</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {symptom.analysis.treatment_suggestions?.slice(0, 2).map((treatment: string, index: number) => (
                              <span key={index} className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded">
                                {treatment}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No symptoms found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || severityFilter !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Start by reporting your first symptoms'
              }
            </p>
            {!searchTerm && severityFilter === 'all' && (
              <Link to="/symptoms/report" className="btn-primary">
                Report Your First Symptoms
              </Link>
            )}
          </div>
        )}
      </div>

      {/* Statistics */}
      {symptoms && symptoms.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Symptom Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{symptoms.length}</p>
              <p className="text-sm text-gray-600">Total Reports</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-warning-600">
                {symptoms.filter((s: any) => s.severity === 'high' || s.severity === 'critical').length}
              </p>
              <p className="text-sm text-gray-600">High/Critical</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-600">
                {symptoms.filter((s: any) => s.severity === 'medium').length}
              </p>
              <p className="text-sm text-gray-600">Medium</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-secondary-600">
                {symptoms.filter((s: any) => s.severity === 'low').length}
              </p>
              <p className="text-sm text-gray-600">Low</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SymptomsScreen;
