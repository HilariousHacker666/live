from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS
import os
from supabase import create_client, Client
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or 'dev-key-for-campus-live'

# Supabase configuration
# TODO: Set these as environment variables
url: str = "https://zcnxzeccwiwgpmhwudgi.supabase.co" #os.environ.get("SUPABASE_URL")
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpjbnh6ZWNjd2l3Z3BtaHd1ZGdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NzExMTQsImV4cCI6MjA3MzQ0NzExNH0.k15GsiyyAsb8R7FqdabTa9mAWCm-SJPPflpdJkxMs_M" #os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


from flask import session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        if not email:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        response = supabase.table('status_updates').select('*').eq('user_id', email).execute()
        user_data = response.data[0] if response.data else None
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
        current_user = User(user_data['id'], user_data['email'], user_data['is_admin'])
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        if not email:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        response = supabase.table('status_updates').select('*').eq('user_id', email).execute()
        user_data = response.data[0] if response.data else None
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
        current_user = User(user_data['id'], user_data['email'], user_data['is_admin'])
        if not current_user.is_admin:
            flash('You need admin privileges to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    email = session.get('email')
    if email:
        response = supabase.table('users').select('*').eq('email', email).execute()
        user_data = response.data[0] if response.data else None
        if user_data:
            # Mock current user
            class User:
                def __init__(self, id, email, is_admin=False):
                    self.id = id
                    self.email = email
                    self.is_admin = is_admin
                    self.is_authenticated = True
            current_user = User(user_data['id'], user_data['email'], user_data['is_admin'])
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
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            session['email'] = email
            flash('Logged in successfully.')
            return redirect(url_for('profile'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Store password in plain text
        response = supabase.table('users').insert({"email": email, "password": password}).execute()
        if response.data:
            flash('Registered successfully. Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Registration failed.')
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    email = session.get('email')
    response = supabase.table('status_updates').select('*').eq('user_id', email).execute()
    user_data = response.data[0] if response.data else None
    return render_template('profile.html', user=user_data)

@app.route('/admin')
#@admin_required
def admin():
    users_response = supabase.table('status_updates').select('*').execute()
    users_data = users_response.data if users_response.data else None

    resources_response = supabase.table('resources').select('*').execute()
    resources_data = resources_response.data if resources_response.data else None

    return render_template('admin.html', users_data=users_data, resources_data=resources_data)

@app.route('/logout')
def logout():
    # In a real application, you would clear the session here
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/api/resources')
def get_resources():
  response = supabase.table('resources').select('*').execute()
  return jsonify(response.data)

@app.route('/api/update-status', methods=['POST'])
def update_status():
  try:
    data = request.json
    response = supabase.table('status_updates').insert(data).execute()
    return jsonify(response.data)
  except Exception as e:
    return jsonify({'error': str(e)}), 500
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True)
