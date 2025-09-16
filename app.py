from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_cors import CORS
import os
import requests
import json
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or 'dev-key-for-campus-live'
CORS(app)

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://zcnxzeccwiwgpmhwudgi.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpjbnh6ZWNjd2l3Z3BtaHd1ZGdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NzExMTQsImV4cCI6MjA3MzQ0NzExNH0.k15GsiyyAsb8R7FqdabTa9mAWCm-SJPPflpdJkxMs_M"

def supabase_query(table, method="GET", data=None, filters=None, eq_filters=None):
    """
    Make requests to Supabase REST API
    """
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    # Add filters if provided
    if filters:
        url += "?" + "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
    
    if eq_filters:
        if "?" in url:
            url += "&" + "&".join([f"{k}=eq.{v}" for k, v in eq_filters.items()])
        else:
            url += "?" + "&".join([f"{k}=eq.{v}" for k, v in eq_filters.items()])
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.RequestException as e:
        print(f"Supabase request error: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        if not email:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        
        response = supabase_query('status_updates', filters={'user_id': email})
        user_data = response[0] if response and len(response) > 0 else None
        
        if not user_data:
            flash('User not found.')
            return redirect(url_for('login'))
        
        # Mock current user
        class User:
            def __init__(self, id, email, is_admin=False):
                self.id = id
                self.email = email
                self.is_admin = is_admin
                self.is_authenticated = True
        
        current_user = User(user_data['id'], user_data['email'], user_data.get('is_admin', False))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        if not email:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        
        response = supabase_query('status_updates', filters={'user_id': email})
        user_data = response[0] if response and len(response) > 0 else None
        
        if not user_data:
            flash('User not found.')
            return redirect(url_for('login'))
        
        # Mock current user
        class User:
            def __init__(self, id, email, is_admin=False):
                self.id = id
                self.email = email
                self.is_admin = is_admin
                self.is_authenticated = True
        
        current_user = User(user_data['id'], user_data['email'], user_data.get('is_admin', False))
        
        if not current_user.is_admin:
            flash('You need admin privileges to access this page.')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    email = session.get('email')
    if email:
        response = supabase_query('users', filters={'email': email})
        user_data = response[0] if response and len(response) > 0 else None
        if user_data:
            # Mock current user
            class User:
                def __init__(self, id, email, is_admin=False):
                    self.id = id
                    self.email = email
                    self.is_admin = is_admin
                    self.is_authenticated = True
            current_user = User(user_data['id'], user_data['email'], user_data.get('is_admin', False))
            return dict(current_user=current_user)
    return dict(current_user=None)

@app.route('/')
def index():
    # Fetch data for index page from Supabase if needed
    return render_template('index.html')

@app.route('/about')
def about():
    # Fetch data for about page from Supabase if needed
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Authenticate using Supabase Auth REST API
        auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        auth_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(auth_url, headers=headers, json=auth_data)
            if response.status_code == 200:
                session['email'] = email
                flash('Logged in successfully.')
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials.')
        except Exception as e:
            flash('Login failed. Please try again.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Register using Supabase Auth REST API
        auth_url = f"{SUPABASE_URL}/auth/v1/signup"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        auth_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(auth_url, headers=headers, json=auth_data)
            if response.status_code == 200:
                # Also add to users table
                user_data = {
                    "email": email,
                    "password": password  # Note: In production, never store plain text passwords
                }
                supabase_query('users', method='POST', data=user_data)
                
                flash('Registered successfully. Please log in.')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. User might already exist.')
        except Exception as e:
            flash('Registration failed. Please try again.')
    
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    email = session.get('email')
    response = supabase_query('status_updates', filters={'user_id': email})
    user_data = response[0] if response and len(response) > 0 else None
    return render_template('profile.html', user=user_data)

@app.route('/admin')
@admin_required
def admin():
    users_response = supabase_query('status_updates')
    users_data = users_response if users_response else []

    resources_response = supabase_query('resources')
    resources_data = resources_response if resources_response else []

    return render_template('admin.html', users_data=users_data, resources_data=resources_data)

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/api/resources')
def get_resources():
    response = supabase_query('resources')
    return jsonify(response if response else [])

@app.route('/api/update-status', methods=['POST'])
def update_status():
    try:
        data = request.json
        response = supabase_query('status_updates', method='POST', data=data)
        return jsonify(response if response else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
