var accessToken;
var urlOnStop;
let fileSet = new Set();
let urlSet = new Set();
var baseUrl = "https://www.futurelearn.com/courses/more-data-mining-with-weka/2/steps";
var todoUrl = "https://www.futurelearn.com/courses/more-data-mining-with-weka/2/todo";

chrome.browserAction.onClicked.addListener(
	function(tab) { 
		console.log("starting process ...");
		chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
		    chrome.tabs.sendMessage(tabs[0].id, {action: "start process"}, function(response) {});  
		});
	}
);

chrome.runtime.onMessage.addListener( function(request, sender, sendResponse){
	if(request.action == 'start-process'){

		var urlGet = request.url;
		var bodyContent = request.body;
		var div = document.createElement('div');
		div.innerHTML = bodyContent;

		console.log("processing first page...");
		if(urlGet.startsWith(todoUrl)){	
			formatResponseTodo(urlGet, removeScripts(bodyContent));
		} else {
			formatResponse(urlGet, removeScripts(bodyContent));
		}
		console.log("walking all other pages...");
		walk(request.url, div, scrape);
		console.log("saving all pages...");
		saveAllPages();
		console.log("process complete!");
	}
});