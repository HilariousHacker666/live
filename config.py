import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-campus-live'
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://zcnxzeccwiwgpmhwudgi.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpjbnh6ZWNjd2l3Z3BtaHd1ZGdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NzExMTQsImV4cCI6MjA3MzQ0NzExNH0.k15GsiyyAsb8R7FqdabTa9mAWCm-SJPPflpdJkxMs_M'