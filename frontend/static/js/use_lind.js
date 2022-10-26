function go() {
	const lind_id = document.getElementById('id-input').value;
	fetch(`/api/${lind_id}`)
	.then(response => {
		if (!response.ok) {
			return Promise.reject(response.status);
		}
		// lind found
		window.location.href = window.location.origin + `/${lind_id}`;
	})
	.catch(e => {
		if (e === 404) {
			// lind not found
			const error = document.getElementById('error-message');
			error.classList.remove('hidden');
			error.innerText = '*Lind not found :(';
		} else {
			// lind found
			window.location.href = `/${lind_id}`;
		};
	});
	return
};

// code run on load

document.getElementById('go-form').setAttribute('action','javascript:go();');