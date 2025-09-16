// Supabase initialization
const supabaseUrl = 'https://zcnxzeccwiwgpmhwudgi.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpjbnh6ZWNjd2l3Z3BtaHd1ZGdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NzExMTQsImV4cCI6MjA3MzQ0NzExNH0.k15GsiyyAsb8R7FqdabTa9mAWCm-SJPPflpdJkxMs_M';

let supabase; // Declare supabase variable globally

// DOM elements
const resourcesContainer = document.getElementById('resources-container');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const updateModal = document.getElementById('update-modal');
const closeModal = document.querySelector('.close');
const updateForm = document.getElementById('update-form');

// State
let currentUser = null;
let resources = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', initApp);

function initApp() {
    //console.log('initApp() called'); // Add this line
    supabase = window.supabase.createClient(supabaseUrl, supabaseKey); // Initialize supabase
    checkAuthState();
    loadResources();
    setupEventListeners();
}

function setupEventListeners() {
    loginBtn.addEventListener('click', handleLogin);
    document.getElementById('signup-btn').addEventListener('click', handleSignup);
    logoutBtn.addEventListener('click', handleLogout);
    searchBtn.addEventListener('click', handleSearch);
    closeModal.addEventListener('click', () => updateModal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === updateModal) updateModal.style.display = 'none';
    });
    updateForm.addEventListener('submit', handleStatusUpdate);
}

// Authentication functions
async function checkAuthState() {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
        currentUser = user;
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
    } else {
        currentUser = null;
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
    }
}

async function handleLogin() {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;

    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
    });

    if (error) console.error('Login error:', error.message);
    else console.log('Login successful:', data);
}

async function handleSignup() {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const confirmPassword = document.getElementById('password-confirm').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
    });

    if (error) console.error('Signup error:', error.message);
    else console.log('Signup successful:', data);
}

async function handleLogout() {
    const { error } = await supabase.auth.signOut();
    if (error) console.error('Logout error:', error.message);
}

// Resource functions
async function loadResources() {
    try {
        const { data, error } = await supabase
            .from('resources')
            .select(`
                *,
                status_updates (crowd_level, chips_available, queue_length, status_message),
                comments (count),
                upvotes (count)
            `)
            .order('created_at', { ascending: false });

        if (error) throw error;

        resources = data;
        //console.log('Resources loaded:', resources); // Add this line
        renderResources(resources);
    } catch (error) {
        console.error('Error loading resources:', error); // Modified this line
        console.error('Error loading resources:', error.message);
    }
}

function renderResources(resourcesToRender) {
    //console.log('Rendering resources:', resourcesToRender); // Add this line
    resourcesContainer.innerHTML = '';

    resourcesToRender.forEach(resource => {
        const latestStatus = resource.status_updates[0] || {};
        
        const resourceCard = document.createElement('div');
        resourceCard.className = 'resource-card';
        resourceCard.innerHTML = `
            <div class="resource-header">
                <h2 class="resource-name">${resource.name}</h2>
                <div class="upvotes">${resource.upvotes[0]?.count || 0} upvotes</div>
            </div>
            <img src="/static/images/${resource.image_url}" alt="${resource.name}" class="resource-image">
            <p class="status-message">${latestStatus.status_message || 'No status updates'}</p>
            <div class="status-tags">
                <span class="tag crowd-tag">Crowd: ${latestStatus.crowd_level || 'Unknown'}</span>
                <span class="tag chips-tag">Chips: ${latestStatus.chips_available || 'Unknown'}</span>
                <span class="tag queue-tag">Queue: ${latestStatus.queue_length || 'Unknown'}</span>
            </div>
            <div class="resource-actions">
                <div class="comments-count">${resource.comments[0]?.count || 0} comments</div>
                ${currentUser ? `<button class="update-btn" data-id="${resource.id}">Update Status</button>` : ''}
            </div>
        `;
        
        resourcesContainer.appendChild(resourceCard);
    });

    // Add event listeners to update buttons
    document.querySelectorAll('.update-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const resourceId = e.target.getAttribute('data-id');
            openUpdateModal(resourceId);
        });
    });
}

function openUpdateModal(resourceId) {
    document.getElementById('resource-id').value = resourceId;
    updateModal.style.display = 'block';
}

async function handleStatusUpdate(e) {
    e.preventDefault();
    
    const resourceId = document.getElementById('resource-id').value;
    const statusMessage = document.getElementById('status-message').value;
    const crowdLevel = document.getElementById('crowd-level').value;
    const chipsAvailable = document.getElementById('chips-available').value;
    const queueLength = document.getElementById('queue-length').value;

    try {
        const { error } = await supabase
            .from('status_updates')
            .insert([
                {
                    resource_id: resourceId,
                    status_message: statusMessage,
                    crowd_level: crowdLevel,
                    chips_available: chipsAvailable,
                    queue_length: queueLength,
                    user_id: currentUser.id
                }
            ]);

        if (error) throw error;

        alert('Status updated successfully!');
        updateModal.style.display = 'none';
        updateForm.reset();
        loadResources(); // Reload resources to show the update
    } catch (error) {
        console.error('Error updating status:', error.message);
        alert('Failed to update status. Please try again.');
    }
}

function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    
    if (!searchTerm) {
        renderResources(resources);
        return;
    }
    
    const filteredResources = resources.filter(resource => 
        resource.name.toLowerCase().includes(searchTerm) ||
        (resource.status_updates[0]?.status_message || '').toLowerCase().includes(searchTerm)
    );
    
    renderResources(filteredResources);
}

// Listen for real-time updates
supabase
    .channel('resource-updates')
    .on('postgres_changes', 
        { 
            event: 'INSERT', 
            schema: 'public', 
            table: 'status_updates' 
        }, 
        (payload) => {
            //console.log('New update received!', payload);
            loadResources(); // Reload resources when a new update is received
        }
    )
    .subscribe();