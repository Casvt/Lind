function toggleEditWindow() {
	const edit_window = document.getElementById('edit-window');
	if (edit_window.getAttribute('aria-hidden') === 'true') {
		edit_window.setAttribute('aria-hidden','false');
	} else {
		edit_window.setAttribute('aria-hidden','true');
	};
	document.querySelector('body').toggleAttribute('show-edit');
	return
};

function saveEdits() {
	var data = {
		'url': document.getElementById('url-input').value,
		'expiration_time': document.getElementById('expiration-time-input').value,
		'limit_usage': parseInt(document.getElementById('limit-usage-input').value)
	};
	if (document.getElementById('access-password-input').value !== null) {
		data.access_password = document.getElementById('access-password-input').value;
	};
	if (document.getElementById('admin-password-input').value !== null) {
		data.admin_password = document.getElementById('admin-password-input').value;
	};
	const pw = document.getElementById('password-input').value;
	fetch(`/api/${lind_id}/manage?admin_password=${pw}`, {
		'method': 'PUT',
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
		document.getElementById('expiration-error').classList.add('hidden');
		toggleEditWindow();
	})
	.catch(e => {
		if (e === 'InvalidExpirationTime') {
			document.getElementById('expiration-error').classList.remove('hidden');
		};
	});
	return
};

function login() {
	const pw = document.getElementById('password-input').value;
	fetch(`/api/${lind_id}/manage?admin_password=${pw}`)
	.then(response => {
		// catch errors
		if (!response.ok) {
			return Promise.reject(response.status);
		};
		document.getElementById('error-message').classList.add('hidden');
		return response.json();
	})
	.then(json => {
		toggleEditWindow();
		document.getElementById('url-input').value = json.result.url;
		if (json.result.expiration_time) {
			var d = new Date(json.result.expiration_time * 1000);
			var date = d.toLocaleString('en-CA').slice(0,10) + 'T' + d.toTimeString().slice(0,5)
			document.getElementById('expiration-time-input').value = date;
		};
		if (json.result.limit_usage) {
			document.getElementById('limit-usage-input').value = json.result.limit_usage;
		};
		document.getElementById('access-password-input').value = '';
		document.getElementById('admin-password-input').value = '';
	})
	.catch(e => {
		if (e === 401) {
			// password incorrect
			const error = document.getElementById('error-message');
			error.classList.remove('hidden');
			error.innerText = '*Password incorrect';
		};
	});
};

// code run on load

const lind_id = window.location.href.split('/').at(-2);

document.getElementById('login-form').setAttribute('action','javascript:login();');
document.getElementById('cancel-button').addEventListener('click', e => toggleEditWindow());
document.getElementById('edit-form').setAttribute('action', 'javascript:saveEdits();')