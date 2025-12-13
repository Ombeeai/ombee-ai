// Ombee AI Configuration

// Supabase Configuration
const SUPABASE_URL = 'https://bwmsjarjrgqtvgqfypyi.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3bXNqYXJqcmdxdHZncWZ5cHlpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzMDQ3MDUsImV4cCI6MjA4MDg4MDcwNX0.S6b7139KSs0SvLf-rwKJVE2SAddr_tzL2yVclBwPNB4';

// API Configuration
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocal ? 'http://localhost:8000' : 'https://ombee-api.onrender.com';

// Initialize Supabase client
window.OmbeeConfig = {
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    API_URL,
    supabase: window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
};