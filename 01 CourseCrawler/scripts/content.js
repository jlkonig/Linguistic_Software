
chrome.runtime.onMessage.addListener( function(request, sender, sendResponse){
	if(request.action == 'start process'){
		console.log("starting process ...");
		var urlStart = window.location.href;
		var fileName = urlStart.replace(/\W+/g, '') + '.txt';
		var body = document.body.innerHTML;
		chrome.runtime.sendMessage({action: 'start-process', url: urlStart, body: body}, function(response) {});
	}
});





