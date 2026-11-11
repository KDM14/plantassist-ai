// Determine API base URL dynamically for local-network access.
// If VITE_API_URL is set in .env, use it. Otherwise auto-detect: same host, port 8000.
const getApiBase = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:8000`;
};

const API_BASE = getApiBase();

export async function sendMessage(question, conversationId = null) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, conversation_id: conversationId }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }
  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export async function getDocuments() {
  const response = await fetch(`${API_BASE}/api/documents`);
  if (!response.ok) throw new Error('Failed to fetch documents');
  return response.json();
}

export async function triggerIngest(force = false) {
  const response = await fetch(`${API_BASE}/api/documents/ingest?force=${force}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Ingest failed');
  return response.json();
}
