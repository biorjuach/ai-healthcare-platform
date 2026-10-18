// Script to manually set authentication token for testing
// Run this in the browser console when on the doctor dashboard

async function setAuthToken() {
  try {
    // Login to get token
    const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'doctor1',
        password: 'password123'
      })
    });
    
    const loginData = await loginResponse.json();
    
    if (loginData.success) {
      // Set token and user data in localStorage
      localStorage.setItem('authToken', loginData.data.token);
      localStorage.setItem('user', JSON.stringify(loginData.data.user));
      
      console.log('✅ Authentication token set successfully!');
      console.log('Token:', loginData.data.token);
      console.log('User:', loginData.data.user);
      
      // Reload the page to refresh the dashboard
      window.location.reload();
    } else {
      console.error('❌ Login failed:', loginData.message);
    }
  } catch (error) {
    console.error('❌ Error setting auth token:', error);
  }
}

// Run the function
setAuthToken();
