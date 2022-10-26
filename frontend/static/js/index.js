function create() {
	const url = document.getElementById('url-input').value;
	fetch(`/api/create`, {
		'method': 'POST',
		'body': JSON.stringify({'url': url}),
		'headers': {"Content-Type": 'application/json'}
	})
	.then(response => {
		return response.json();
	})
	.then(json => {
		window.location.href = `/${json.result.lind_id}/show`;
	})
	return
};

// code run on load

document.getElementById('create-form').setAttribute('action','javascript:create();');