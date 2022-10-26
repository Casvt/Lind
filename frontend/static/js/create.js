function createLind() {
	var data = {
		'url': document.getElementById('url-input').value,
		'expiration_time': document.getElementById('expiration-time-input').value,
		'limit_usage': parseInt(document.getElementById('limit-usage-input').value),
		'access_password': document.getElementById('access-password-input').value,
		'admin_password': document.getElementById('admin-password-input').value
	};
	fetch(`/api/create`, {
		'method': 'POST',
		'body': JSON.stringify(data),
		'headers': {'Content-Type': 'application/json'}
	})
	.then(response => {
		return response.json();
	})
	.then(json => {
		// catch errors
		if (json.error !== null) {
			return Promise.reject(json.error);
		};
		window.location.href = `/${json.result.lind_id}/show`;
	})
	.catch(e => {
		if (e === 'InvalidExpirationTime') {
			document.getElementById('expiration-error').classList.remove('hidden');
		};
	});
	return
};

// code run on load

document.getElementById('create-form').setAttribute('action', 'javascript:createLind();')