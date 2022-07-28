function toggleAdvanced() {
	document.querySelectorAll('.advanced-setting').forEach(e => {
		e.classList.toggle('hidden');
	});
	document.querySelectorAll('.basic-setting').forEach(e => {
		e.classList.toggle('expanded');
	});
	document.getElementById('create-form').classList.toggle('advanced');
}

document.getElementById('show-advanced').addEventListener('click', toggleAdvanced);
