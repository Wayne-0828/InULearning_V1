const apiClient = {
	baseUrl: 'http://localhost/api/v1',
	getToken() {
		return (
			localStorage.getItem('auth_token') ||
			sessionStorage.getItem('auth_token') ||
			localStorage.getItem('teacher_token') ||
			sessionStorage.getItem('teacher_token') ||
			''
		);
	},
	async request(path, options = {}) {
		const url = `${this.baseUrl}${path}`;
		const headers = Object.assign({ 'Content-Type': 'application/json', 'Accept': 'application/json' }, options.headers || {});
		const token = this.getToken();
		if (token) headers['Authorization'] = `Bearer ${token}`;
		const res = await fetch(url, { ...options, headers });
		let data = {};
		try { data = await res.json(); } catch (_) {}
		if (!res.ok) {
			if (res.status === 401) {
				localStorage.removeItem('auth_token');
				sessionStorage.removeItem('auth_token');
				localStorage.removeItem('teacher_token');
				sessionStorage.removeItem('teacher_token');
			}
			throw new Error(data.detail || data.message || 'Request failed');
		}
		return data;
	},
	get(path) { return this.request(path, { method: 'GET' }); },
	post(path, body) { return this.request(path, { method: 'POST', body: JSON.stringify(body) }); },
	put(path, body) { return this.request(path, { method: 'PUT', body: JSON.stringify(body) }); },
	delete(path) { return this.request(path, { method: 'DELETE' }); },
};

window.apiClient = apiClient;

