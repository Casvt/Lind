// code run on load

const lind_id = window.location.href.split('/').at(-2);

document.getElementById('action-use').setAttribute('href', window.location.origin + '/' + lind_id);
document.getElementById('action-manage').setAttribute('href', window.location.origin + '/' + lind_id + '/manage');
document.getElementById('title').innerText = window.location.origin + '/' + lind_id;