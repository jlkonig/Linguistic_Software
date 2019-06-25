// Move recursively through the DOM of one page.
function walk(urlRoot,node,func) {

	if(node.nodeName == "A"){
		func(urlRoot,node)
	}

	var children = node.childNodes;
	for(child of children){
		walk(urlRoot,child, func);
	}
};

function scrape(urlRoot,node){

	var urlGet = "https://www.futurelearn.com" + node.getAttribute('href');

	if(urlGet.startsWith(baseUrl) && urlGet.indexOf('#') === -1 && urlGet.includes("/comments") != true){

		// Get the next page to be walked
		var response = httpGet(urlRoot, urlGet); 

		if(response != ''){
			// Format and save the next page
			formatResponse(urlGet, removeScripts(response));
		}

		// Walk the next page
		walkNext(urlGet,response);

	} else if(urlGet.startsWith(todoUrl) && urlGet.indexOf('#') === -1 && urlGet.includes("/comments") != true){

		// Get the next page to be walked
		var response = httpGet(urlRoot, urlGet); 

		if(response != ''){
			// Format and save the next page
			formatResponseTodo(urlGet, removeScripts(response));
		}

		// Walk the next page
		walkNext(urlGet,response);
	}
}

function walkNext(urlRoot, response){
	urlOnStop = urlRoot;
	var doc = htmlToElement(response);
	walk(urlRoot,doc,scrape);
}

function htmlToElement(html) {
	var template = document.createElement('template');
	template.innerHTML = html;
	return template.content;
}

function httpGet(urlRoot, urlGet){	
	try{
		if((urlSet.has(urlGet) != true) && urlGet != urlRoot && !urlGet.endsWith("/reveal")){
			console.log("Getting " + urlGet)
			wait(-1);
			urlSet.add(urlGet);
		    var xmlHttp = new XMLHttpRequest();
		    xmlHttp.open( "GET", urlGet, false );
		    xmlHttp.send( null );
		    return xmlHttp.responseText;
		} else {
			console.log("-next already seen, skipping page ...");
		}
	} catch(err) {
		console.log('Failed to execute send on XMLHttpRequest');
	} 
	return '';
}

function httpPost(fileName, fileContent){	
	try{
		if((fileSet.has(fileName) != true) && fileContent != ''){
			//console.log("Saving " + fileName)
			fileSet.add(fileName);
			saveText(fileName, fileContent);
		}
	} catch(err) {
		console.log(err);
	} 
}

function removeScripts(response){
	try{
		var div = document.createElement('div');
		div.innerHTML = response;
		var scripts = div.getElementsByTagName('script');
		var i = scripts.length;
		while(i--){
			scripts[i].parentNode.removeChild(scripts[i]);
		}
		return div.innerHTML;
	} catch (err) {
		return '';
	}
}

function wait(ms){
	if(ms == -1){
		// 1000 = 1 sec, 3000 = 3 sec
		var min = 1000; var max = 3000;
		ms = Math.floor(Math.random() * (max - min + 1)) + min;
	}

	var start = new Date().getTime();
	var end = start;
	while(end < start + ms) {
		end = new Date().getTime();
	}
}

function saveText(filename, text) {
    var tempElem = document.createElement('a');
    tempElem.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    tempElem.setAttribute('download', filename);
    tempElem.click();
 }
