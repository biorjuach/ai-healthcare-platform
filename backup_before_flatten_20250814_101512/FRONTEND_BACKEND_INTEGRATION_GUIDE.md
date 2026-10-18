# Frontend-Backend Integration Guide
## Ensuring Real-Time Updates Without Blank Screens

This guide provides a comprehensive solution for ensuring that backend changes reflect immediately in the frontend without causing blank screens or poor user experience.

## 🎯 Overview

The solution implements a robust, fault-tolerant architecture with:
- **Real-time connection monitoring**
- **Automatic retry mechanisms**
- **Graceful fallbacks**
- **Error recovery**
- **Connection status indicators**

## 🏗️ Architecture Components

### 1. Robust API Service Layer (`mobile/src/services/apiService.ts`)

**Features:**
- Automatic retry on network failures
- Connection health monitoring
- Request/response interceptors
- Error classification and handling
- Timeout management

**Key Capabilities:**
```typescript
// Automatic retry with exponential backoff
const API_CONFIG = {
  retryAttempts: 3,
  retryDelay: 1000,
  healthCheckInterval: 30000,
};

// Error classification
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
}
```

### 2. Connection Status Component (`mobile/src/components/ConnectionStatus.tsx`)

**Features:**
- Real-time connection monitoring
- Visual status indicators
- Automatic retry buttons
- Pulsing animation for connection issues
- Dismissible notifications

**Usage:**
```tsx
<ConnectionStatusComponent 
  onRetry={() => {
    // Retry failed operations
    if (analysisError) retryAnalysis();
    if (submitError) retrySubmit();
  }}
  showDetails={true}
/>
```

### 3. Custom API Hooks (`mobile/src/hooks/useApiCall.ts`)

**Features:**
- Automatic data fetching
- Loading states
- Error handling
- Retry mechanisms
- Connection monitoring

**Usage Examples:**
```tsx
// GET request with auto-retry
const { data, loading, error, refetch } = useGet('/patients/1/');

// POST request with fallback data
const { data, loading, error, retry } = usePost('/symptoms/analyze/', {
  symptoms: symptomText,
  language: selectedLanguage,
}, {
  fallbackData: defaultAnalysis,
  retryOnError: true,
  retryAttempts: 3,
});
```

## 🔄 Real-Time Update Mechanisms

### 1. Health Check Endpoint

**Backend:** `GET /api/health/`
```python
@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for connection monitoring"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check ML model availability
        ml_model_status = "available" if symptom_analyzer.ml_model else "unavailable"
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'ml_model': ml_model_status,
            'response_time': time.time() - start_time,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)
```

### 2. Automatic Retry Logic

**Frontend Implementation:**
```typescript
private shouldRetry(error: AxiosError): boolean {
  return (
    error.code === 'ECONNABORTED' ||
    error.message.includes('timeout') ||
    (!error.response && error.code !== 'ERR_CANCELED') ||
    (error.response && error.response.status >= 500)
  );
}
```

### 3. Connection Monitoring

**Continuous Health Checks:**
```typescript
private startHealthCheck() {
  this.healthCheckInterval = setInterval(async () => {
    try {
      const startTime = Date.now();
      await this.axiosInstance.get('/health/');
      this.updateConnectionStatus(true, Date.now() - startTime);
    } catch (error) {
      this.updateConnectionStatus(false, 0, 'Health check failed');
    }
  }, API_CONFIG.healthCheckInterval);
}
```

## 🛡️ Error Handling & Fallbacks

### 1. Graceful Degradation

**When Backend is Unavailable:**
- Show cached data if available
- Display offline mode indicators
- Provide retry options
- Queue operations for later sync

**Implementation:**
```tsx
const { data, loading, error, isConnected } = useGet('/patients/1/', {
  fallbackData: cachedPatientData,
  retryOnError: true,
});

// Show offline indicator when disconnected
{!isConnected && (
  <OfflineIndicator 
    message="Working offline - data will sync when connected"
  />
)}
```

### 2. Error Recovery

**Automatic Recovery:**
- Re-connect when network is restored
- Retry failed operations
- Clear error states
- Update UI accordingly

**Manual Recovery:**
- Retry buttons for user-initiated recovery
- Clear error options
- Refresh data functionality

## 📱 Mobile App Integration

### 1. Updated SymptomReportScreen

**Before (Fragile):**
```tsx
const analyzeSymptoms = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/symptoms/analyze/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms: symptomText }),
    });
    const data = await response.json();
    setAnalysis(data);
  } catch (error) {
    Alert.alert('Error', 'Failed to connect to server');
  }
};
```

**After (Robust):**
```tsx
const {
  data: analysisData,
  loading: isAnalyzing,
  error: analysisError,
  retry: retryAnalysis,
} = usePost('/symptoms/analyze/', {
  symptoms: symptomText,
  language: selectedLanguage,
}, {
  autoFetch: false,
  retryOnError: true,
  retryAttempts: 3,
  onSuccess: (data) => {
    setAnalysis(data);
    if (data.is_emergency) {
      Alert.alert('EMERGENCY ALERT', 'Seek immediate medical attention');
    } else {
      setCurrentStep(3);
    }
  },
  onError: (error) => {
    Alert.alert('Error', error || 'Failed to analyze symptoms');
  },
});
```

### 2. Connection Status Integration

```tsx
return (
  <SafeAreaView style={styles.container}>
    <ConnectionStatusComponent 
      onRetry={() => {
        if (analysisError) retryAnalysis();
        if (submitError) retrySubmit();
      }}
      showDetails={true}
    />
    {/* Rest of the component */}
  </SafeAreaView>
);
```

## 🖥️ Admin Dashboard Integration

### 1. Enhanced Dashboard Component

**Real-time Updates:**
```tsx
const fetchDashboardData = async () => {
  try {
    setLoading(true);
    setError(null);
    
    // Check backend connection
    const statsResponse = await fetch('/api/analytics/dashboard/');
    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      setSystemStats(statsData);
      setBackendConnected(true);
    } else {
      // Fallback to mock data
      setBackendConnected(false);
      setSystemStats(mockSystemStats);
    }
  } catch (error) {
    setBackendConnected(false);
    setError('Could not connect to backend');
    setSystemStats(mockSystemStats);
  } finally {
    setLoading(false);
  }
};
```

### 2. Auto-refresh Mechanism

```tsx
useEffect(() => {
  fetchDashboardData();
  const interval = setInterval(fetchDashboardData, 30000); // 30 seconds
  return () => clearInterval(interval);
}, []);
```

## 🔧 Configuration

### 1. Environment Variables

**Mobile App (`mobile/src/config.ts`):**
```typescript
export const API_CONFIG = {
  baseURL: API_URL,
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000,
  healthCheckInterval: 30000,
};
```

**Backend (`backend/settings.py`):**
```python
# API Configuration
API_TIMEOUT = 10
API_RETRY_ATTEMPTS = 3
API_HEALTH_CHECK_INTERVAL = 30

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:19006",
    "exp://localhost:19000",
]
```

### 2. Error Handling Configuration

```typescript
// Error thresholds
const ERROR_THRESHOLDS = {
  maxRetries: 3,
  retryDelay: 1000,
  connectionTimeout: 10000,
  healthCheckInterval: 30000,
};

// Error messages
const ERROR_MESSAGES = {
  network: 'Network error. Please check your connection.',
  server: 'Server error. Please try again later.',
  timeout: 'Request timed out. Please try again.',
  auth: 'Authentication required. Please log in again.',
};
```

## 🚀 Deployment Considerations

### 1. Production Configuration

**Environment-specific settings:**
```typescript
const isProduction = process.env.NODE_ENV === 'production';

export const API_CONFIG = {
  baseURL: isProduction ? 'https://api.healthcare.com' : 'http://localhost:8000',
  timeout: isProduction ? 15000 : 10000,
  retryAttempts: isProduction ? 5 : 3,
  healthCheckInterval: isProduction ? 60000 : 30000,
};
```

### 2. Monitoring and Logging

**Frontend Logging:**
```typescript
private logError(error: ApiError) {
  console.error('API Error:', {
    type: error.type,
    message: error.message,
    statusCode: error.statusCode,
    timestamp: new Date().toISOString(),
  });
  
  // Send to monitoring service in production
  if (process.env.NODE_ENV === 'production') {
    // analytics.track('api_error', error);
  }
}
```

**Backend Logging:**
```python
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    try:
        # Health check logic
        logger.info("Health check successful")
        return JsonResponse({'status': 'healthy'})
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({'status': 'unhealthy'}, status=500)
```

## 📊 Performance Monitoring

### 1. Response Time Tracking

```typescript
private updateConnectionStatus(isConnected: boolean, responseTime: number) {
  this.connectionStatus = {
    isConnected,
    lastCheck: new Date(),
    responseTime,
  };
  
  // Track performance metrics
  if (responseTime > 5000) {
    console.warn(`Slow API response: ${responseTime}ms`);
  }
}
```

### 2. Error Rate Monitoring

```typescript
private errorCount = 0;
private successCount = 0;

private trackRequest(success: boolean) {
  if (success) {
    this.successCount++;
  } else {
    this.errorCount++;
  }
  
  const errorRate = this.errorCount / (this.errorCount + this.successCount);
  if (errorRate > 0.1) { // 10% error rate
    console.warn(`High error rate detected: ${(errorRate * 100).toFixed(1)}%`);
  }
}
```

## 🔄 Continuous Integration

### 1. Automated Testing

**API Service Tests:**
```typescript
describe('ApiService', () => {
  it('should retry failed requests', async () => {
    // Test retry logic
  });
  
  it('should handle network errors gracefully', async () => {
    // Test error handling
  });
  
  it('should monitor connection status', async () => {
    // Test health checks
  });
});
```

### 2. Health Check Monitoring

**Automated Health Checks:**
```bash
#!/bin/bash
# health_check.sh

while true; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health/)
  if [ $response -ne 200 ]; then
    echo "Health check failed: $response"
    # Send alert
  fi
  sleep 30
done
```

## 🎯 Best Practices

### 1. User Experience

- **Always show loading states** during API calls
- **Provide clear error messages** with actionable steps
- **Offer retry options** for failed operations
- **Show connection status** to keep users informed
- **Cache data** for offline functionality

### 2. Error Handling

- **Classify errors** appropriately (network, server, auth, etc.)
- **Implement exponential backoff** for retries
- **Provide fallback data** when possible
- **Log errors** for debugging and monitoring
- **Graceful degradation** when services are unavailable

### 3. Performance

- **Monitor response times** and set alerts
- **Implement request caching** where appropriate
- **Use connection pooling** for database operations
- **Optimize payload sizes** for mobile networks
- **Implement request deduplication** for concurrent calls

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **Blank Screens**
   - **Cause:** API failures without fallbacks
   - **Solution:** Implement fallback data and error boundaries

2. **Slow Loading**
   - **Cause:** Network timeouts or server issues
   - **Solution:** Implement loading states and retry mechanisms

3. **Connection Loss**
   - **Cause:** Network instability
   - **Solution:** Real-time connection monitoring and auto-retry

4. **Data Staleness**
   - **Cause:** Cached data not updated
   - **Solution:** Implement cache invalidation and refresh mechanisms

## 📈 Monitoring Dashboard

Create a monitoring dashboard to track:
- API response times
- Error rates
- Connection status
- User experience metrics
- System health indicators

This comprehensive solution ensures that your healthcare platform remains responsive and reliable, even when backend changes occur or network issues arise.
