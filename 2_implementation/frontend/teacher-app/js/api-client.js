const apiClient = {
	baseUrl: 'http://localhost/api/v1',
	async request(path, options = {}) {
		const url = `${this.baseUrl}${path}`;
		const headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
		const token = localStorage.getItem('auth_token');
		if (token) headers['Authorization'] = `Bearer ${token}`;
		const res = await fetch(url, { ...options, headers });
		const data = await res.json().catch(() => ({}));
		if (!res.ok) throw new Error(data.detail || data.message || 'Request failed');
		return data;
	},
	get(path) { return this.request(path, { method: 'GET' }); },
	post(path, body) { return this.request(path, { method: 'POST', body: JSON.stringify(body) }); },
	put(path, body) { return this.request(path, { method: 'PUT', body: JSON.stringify(body) }); },
	delete(path) { return this.request(path, { method: 'DELETE' }); },
};

window.apiClient = apiClient;

