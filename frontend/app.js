const API_BASE_URL = '';

let authToken = localStorage.getItem('docgen_auth_token');

function getAuthHeaders() {
    return authToken ? { 'Authorization': `Bearer ${authToken}` } : {};
}

// Intercept fetch to add auth headers and handle 401/403
const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    if (!config) config = {};
    if (!config.headers) config.headers = {};
    
    // Don't add token to auth routes
    if (!resource.includes('/api/auth/')) {
        config.headers = { ...config.headers, ...getAuthHeaders() };
    }
    
    const response = await originalFetch(resource, config);
    
    if (response.status === 401 && !resource.includes('/api/auth/')) {
        showAuthModal();
        throw new Error('Unauthorized');
    }
    
    if (response.status === 403) {
        const errorData = await response.json().catch(() => ({}));
        if (errorData.detail === 'FREE_LIMIT_REACHED') {
            showUpgradeModal();
            throw new Error('FREE_LIMIT_REACHED');
        }
    }
    
    return response;
};

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const docForm = document.getElementById('doc-form');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const spinner = generateBtn.querySelector('.spinner');
    
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const previewIframe = document.getElementById('preview-iframe');
    const resultsArea = document.getElementById('results-area');
    
    const copyHtmlBtn = document.getElementById('copy-html-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    
    // Auth UI
    const authModal = document.getElementById('auth-modal');
    const upgradeModal = document.getElementById('upgrade-modal');
    const navAuthBtn = document.getElementById('nav-auth-btn');
    const authForm = document.getElementById('auth-form');
    const toggleAuth = document.getElementById('toggle-auth');
    const authTitle = document.getElementById('auth-title');
    const authBtn = document.getElementById('auth-btn');
    
    let isLogin = true;
    let currentDocHtml = '';
    let currentDocId = null;

    // Check login state
    updateNavUI();
    if (authToken) {
        loadHistory();
    }

    // --- Modal Logic ---
    window.showAuthModal = () => {
        authModal.classList.remove('hidden');
    };
    
    window.showUpgradeModal = () => {
        upgradeModal.classList.remove('hidden');
    };

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.add('hidden');
        });
    });

    toggleAuth.addEventListener('click', (e) => {
        e.preventDefault();
        isLogin = !isLogin;
        authTitle.textContent = isLogin ? 'Sign In' : 'Create Account';
        authBtn.textContent = isLogin ? 'Sign In' : 'Sign Up';
        toggleAuth.textContent = isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in';
    });
    
    navAuthBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (authToken) {
            localStorage.removeItem('docgen_auth_token');
            authToken = null;
            updateNavUI();
            document.getElementById('history-grid').innerHTML = '<p class="empty-state">Please sign in to view history.</p>';
            showToast('Logged out successfully');
        } else {
            showAuthModal();
        }
    });
    
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Authentication failed');
            }
            
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('docgen_auth_token', authToken);
            
            authModal.classList.add('hidden');
            showToast(isLogin ? 'Logged in successfully' : 'Account created!');
            updateNavUI();
            loadHistory();
            
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    function updateNavUI() {
        if (authToken) {
            navAuthBtn.textContent = 'Sign Out';
        } else {
            navAuthBtn.textContent = 'Sign In';
        }
    }
    
    // --- PayPal Subscription Logic ---
    async function initPayPal() {
        try {
            // Get client ID and Plan ID from backend
            const res = await fetch(`${API_BASE_URL}/api/billing/paypal-config`);
            if (!res.ok) return; // Silent fail if paypal isn't configured yet
            
            const config = await res.json();
            
            // Dynamically load the PayPal JS SDK
            const script = document.createElement('script');
            script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&vault=true&intent=subscription`;
            
            script.onload = () => {
                paypal.Buttons({
                    style: {
                        shape: 'rect',
                        color: 'blue',
                        layout: 'vertical',
                        label: 'subscribe'
                    },
                    createSubscription: function(data, actions) {
                        return actions.subscription.create({
                            'plan_id': config.plan_id
                        });
                    },
                    onApprove: async function(data, actions) {
                        showToast('Payment approved! Verifying...', 'success');
                        
                        // Send subscription ID to our backend for verification
                        try {
                            const verifyRes = await fetch(`${API_BASE_URL}/api/billing/verify-paypal-subscription`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ subscription_id: data.subscriptionID })
                            });
                            
                            const verifyData = await verifyRes.json();
                            if (verifyData.status === 'success') {
                                showToast('Welcome to Pro! You now have unlimited documents.', 'success');
                                upgradeModal.classList.add('hidden');
                            } else {
                                showToast(verifyData.message || 'Verification pending.', 'error');
                            }
                        } catch (err) {
                            showToast('Error verifying subscription.', 'error');
                        }
                    }
                }).render('#paypal-button-container');
            };
            
            document.body.appendChild(script);
        } catch (error) {
            console.error("PayPal config error:", error);
        }
    }
    
    // Initialize PayPal buttons when app loads
    initPayPal();

    // --- Document Generation Logic ---
    docForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!authToken) {
            showAuthModal();
            return;
        }
        
        const title = document.getElementById('title').value;
        const document_type = document.getElementById('document_type').value;
        const user_input = document.getElementById('user_input').value;
        const additional_context = document.getElementById('additional_context').value;
        
        const payload = { title, document_type, user_input, additional_context };
        
        // UI Loading state
        generateBtn.disabled = true;
        btnText.textContent = 'Generating...';
        spinner.classList.remove('hidden');
        resultsPlaceholder.classList.add('hidden');
        resultsContent.classList.add('hidden');
        loadingState.classList.remove('hidden');
        
        resultsArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        try {
            const response = await fetch(`${API_BASE_URL}/api/documents/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) throw new Error('Failed to generate document');
            
            const data = await response.json();
            currentDocHtml = data.generated_html || 'No HTML content returned';
            currentDocId = data.id || data.doc_id || null;
            
            // Render in iframe
            previewIframe.srcdoc = currentDocHtml;
            
            // UI Success state
            loadingState.classList.add('hidden');
            resultsContent.classList.remove('hidden');
            showToast('Document generated successfully!', 'success');
            
            loadHistory();
            
        } catch (error) {
            console.error('Error generating document:', error);
            if (error.message !== 'FREE_LIMIT_REACHED' && error.message !== 'Unauthorized') {
                showToast('Error generating document. Please try again.', 'error');
            }
            loadingState.classList.add('hidden');
            resultsPlaceholder.classList.remove('hidden');
        } finally {
            generateBtn.disabled = false;
            btnText.textContent = 'Generate Document';
            spinner.classList.add('hidden');
        }
    });

    copyHtmlBtn.addEventListener('click', () => {
        if (currentDocHtml) {
            navigator.clipboard.writeText(currentDocHtml)
                .then(() => showToast('HTML copied to clipboard!', 'success'))
                .catch(() => showToast('Failed to copy HTML.', 'error'));
        }
    });

    downloadPdfBtn.addEventListener('click', () => {
        if (currentDocId) {
            downloadPdf(currentDocId);
        } else {
            showToast('Cannot download: Document ID not found.', 'error');
        }
    });
});

async function loadHistory() {
    if (!authToken) return;
    const historyGrid = document.getElementById('history-grid');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/`);
        if (!response.ok) throw new Error('Failed to load history');
        
        const data = await response.json();
        const documents = data.documents || data || [];
        
        if (documents && documents.length > 0) {
            historyGrid.innerHTML = '';
            documents.forEach(doc => {
                const card = document.createElement('div');
                card.className = 'history-card';
                card.innerHTML = `
                    <div class="history-card-header">
                        <span class="history-type">${doc.document_type}</span>
                        <span class="history-date">${new Date(doc.created_at || Date.now()).toLocaleDateString()}</span>
                    </div>
                    <h3 class="history-title">${doc.title || 'Untitled Document'}</h3>
                    <div class="history-actions">
                        <button class="btn btn-primary btn-sm" onclick="previewDocument('${doc.id || doc.doc_id}')">Preview</button>
                        <button class="btn btn-secondary btn-sm" onclick="downloadPdf('${doc.id || doc.doc_id}')">PDF</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteDocument('${doc.id || doc.doc_id}')">Delete</button>
                    </div>
                `;
                historyGrid.appendChild(card);
            });
        } else {
            historyGrid.innerHTML = '<p class="empty-state">No documents generated yet.</p>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function previewDocument(docId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/${docId}/html`);
        if (!response.ok) throw new Error('Failed to fetch document HTML');
        
        let htmlContent = '';
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json();
            htmlContent = data.html || data.generated_html || '';
        } else {
            htmlContent = await response.text();
        }

        const previewIframe = document.getElementById('preview-iframe');
        previewIframe.srcdoc = htmlContent;
        
        document.getElementById('results-placeholder').classList.add('hidden');
        document.getElementById('loading-state').classList.add('hidden');
        document.getElementById('results-content').classList.remove('hidden');
        
        const downloadPdfBtn = document.getElementById('download-pdf-btn');
        const newBtn = downloadPdfBtn.cloneNode(true);
        downloadPdfBtn.parentNode.replaceChild(newBtn, downloadPdfBtn);
        newBtn.addEventListener('click', () => downloadPdf(docId));

        const copyHtmlBtn = document.getElementById('copy-html-btn');
        const newCopyBtn = copyHtmlBtn.cloneNode(true);
        copyHtmlBtn.parentNode.replaceChild(newCopyBtn, copyHtmlBtn);
        newCopyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(htmlContent)
                .then(() => showToast('HTML copied to clipboard!', 'success'))
                .catch(() => showToast('Failed to copy HTML.', 'error'));
        });
        
        document.getElementById('results-area').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (error) {
        console.error('Error previewing document:', error);
        showToast('Error loading document preview.', 'error');
    }
}

function downloadPdf(docId) {
    window.open(`${API_BASE_URL}/api/documents/${docId}/pdf`, '_blank');
}

async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/${docId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete document');
        
        showToast('Document deleted successfully', 'success');
        loadHistory();
    } catch (error) {
        console.error('Error deleting document:', error);
        showToast('Error deleting document.', 'error');
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : '⚠';
    toast.innerHTML = `<strong>${icon}</strong> ${message}`;
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => container.removeChild(toast), 300);
    }, 3000);
}

window.previewDocument = previewDocument;
window.downloadPdf = downloadPdf;
window.deleteDocument = deleteDocument;
