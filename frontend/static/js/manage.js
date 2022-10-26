function go() {
	const lind_id = document.getElementById('id-input').value;
	fetch(`/api/${lind_id}/manage?admin_password=abc`)
	.then(response => {
		if (!response.ok) {
			return Promise.reject(response.status);
		};
		// lind found
		window.location.href = `/${lind_id}/manage`;
	})
	.catch(e => {
		if (e === 404 || e === 400) {
			// lind not found
			const error = document.getElementById('error-message');
			error.classList.remove('hidden');
			if (e === 404) {
				error.innerText = '*Lind not found :(';
			} else if (e === 400) {
				error.innerText = '*Lind not manageable :(';
			};
		} else {
			// lind found
			window.location.href = `/${lind_id}/manage`;
		};
	});
	return
};

// code run on load

document.getElementById('go-form').setAttribute('action','javascript:go();');