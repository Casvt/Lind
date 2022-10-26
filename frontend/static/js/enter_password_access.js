function login() {
	const pw = document.getElementById('password-input').value;
	fetch(`/api/${lind_id}?access_password=${pw}`)
	.then(response => {
		// catch errors
		if (!response.ok) {
			return Promise.reject(response.status);
		};
		return response.json();
	})
	.then(json => {
		window.location.href = json.result.url;
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

const lind_id = window.location.href.split('/').at(-1);

document.getElementById('login-form').setAttribute('action','javascript:login();');
