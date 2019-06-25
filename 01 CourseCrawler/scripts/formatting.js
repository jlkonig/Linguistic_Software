//var dictionary = {};
var pages = [];

function trimNewlines(text){
	text = text.replace(/\n+/g, '\n');
	text = text.replace(/^\n+|\n+$/g, '');
	return text;
}

function trimContentNewlines(text){
	text = text.replace(/\n+\s*\n+/g, '\n');
	return text;
}

function formatResponse(urlRoot, response){
	try{
		console.log("formatting response");
		if(response !== null && response !== ''){
			var pageContent = '';
			var formatted = [];

			// Convert response text into document object model
			var el = document.createElement( 'html' );
			el.innerHTML = response;

			// Extract step number
			var stepNumEl = el.getElementsByClassName("a-stepnumber")
			var stepNumText  = trimNewlines(stepNumEl[0].textContent);
			//pageContent = trimNewlines(pageContent);
			//pageContent += stepNumText + "\n";
			var tmp = stepNumText.split(".");
			var stepNum = tmp[0];
			var subStepNum = tmp[1];

			// Extract title
			var titleEl = el.getElementsByClassName("a-article-h1")
			var titleText  = titleEl[0].textContent.split("\n")[1];
			pageContent += titleText + "\n"

			// Find elements within page that determine page type
			var quizEl = el.getElementsByClassName("quiz-container");
			var videoEl = el.getElementsByClassName("video-container");
			var discussionEl = el.getElementsByClassName("discussion-comments-container");
			var pageType = 'Article'
			// Determine if page is "Quiz" and extract quiz content
			if(quizEl.length > 0){
				pageType = 'Quiz';
				formatted = formatQuiz(urlRoot, el);
				pageContent += trimContentNewlines(formatted[1]) + "\n";
				pageContent = "<-- " + stepNumText + " " + pageType + " -->\n" + pageContent;
				pages.push([stepNum, subStepNum, formatted[0], pageContent]);
				console.log("processed step " + stepNumText + "." + formatted[0]);
				return pageContent;
			}
			// Determine if page is "Video"
			else if(videoEl.length > 0){
				pageType = 'Video';
				formatted = formatVideo(el);
				pageContent += trimContentNewlines(formatted[1]) + "\n";
				pageContent = "<-- " + stepNumText + " " + pageType + " -->\n" + pageContent;
				pages.push([stepNum, subStepNum, formatted[0], pageContent]);
				console.log("processed step " + stepNumText);
				return pageContent;
			}
			// Determine if page is "Discussion"
			else if(discussionEl.length > 0){
				pageType = 'Discussion';
			} // Else page is "Article" by default

			// Extract page content (for any page type except "Quiz") 
			formatted = formatOther(el);
			pageContent += trimContentNewlines(formatted[1]) + "\n";
			pageContent = "<-- " + stepNumText + " " + pageType + " -->\n" + pageContent;
			pages.push([stepNum, subStepNum, formatted[0], pageContent]);
			console.log("processed step " + stepNumText);
			return pageContent;
		}
		return '';
	} catch (e) {
		// console.log("Whoops! " + e)
		return '';
	}
}

function formatResponseTodo(urlRoot, response){
	try{
		console.log("formatting response todo");
		if(response !== null && response !== ''){
			var pageContent = '';
			var formatted = [];

			// Convert response text into document object model
			var el = document.createElement( 'html' );
			el.innerHTML = response;

			// Extract step number
			var stepNumText = el.getElementsByClassName("a-stepnumber")[0].textContent.split(".")[0] + ".0";
			//pageContent = trimNewlines(pageContent);
			//pageContent += stepNumText + "\n";
			var tmp = stepNumText.split(".");
			var stepNum = tmp[0];
			var subStepNum = tmp[1];

			// Extract title
			var titleEl = el.getElementsByClassName("headline-strong")
			var titleText  = titleEl[0].title;
			pageContent += titleText + "\n"

			var pageType = 'Todo'

			// Extract page content (for any page type except "Quiz") 
			formatted = formatTodo(el);
			pageContent += trimContentNewlines(formatted[1]) + "\n";
			pageContent = "<-- " + stepNumText + " " + pageType + " -->\n" + pageContent;
			pages.push([stepNum, subStepNum, formatted[0], pageContent]);
			console.log("processed step " + stepNumText);
			return pageContent;
		}
		return '';
	} catch (e) {
		// console.log("Whoops! " + e)
		return '';
	}
}

function formatQuiz(urlRoot, el){
	var quizTuple = extractQuiz(urlRoot, el);
	return quizTuple;
}

function formatVideo(el){
	var articleText = '';
	var contentEl = el.getElementsByClassName("a-text-context")
	for(c of contentEl){
		articleText  += trimNewlines(c.textContent) + "\n";
	}
	var transcriptEl = el.getElementsByClassName("transcript__para")
	if(transcriptEl.length > 0){
		articleText += "<Start Transcript>\n";
	}
	for(t of transcriptEl){
		t.removeChild(t.childNodes[0]);
		articleText  += trimNewlines(t.removeChild(t.childNodes[0]).textContent) + "\n";
	}
	if(transcriptEl.length > 0){
		articleText += "<End Transcript>\n";
	}

	return [0,articleText];
}

function formatTodo(el){
	var articleText = '';
	var contentEl = el.getElementsByClassName("activities list")
	for(c of contentEl){
		articleText  += trimNewlines(c.textContent) + "\n";
	}
	return [0,articleText];
}

function formatOther(el){
	var articleText = '';
	var contentEl = el.getElementsByClassName("a-text-context")
	for(c of contentEl){
		articleText  += trimNewlines(c.textContent) + "\n";
	}
	return [0,articleText];
}

function saveAllPages(){

	// Sort pages
	var allPages = '';
	pages = pages.sort(sortStepFunction);

	// Remove duplicate pages - happens with the last question in each quiz
	var pagesTmp = pages;
	pages = [];
	for (var i = 0; i < pagesTmp.length; i++) {
		if(i == 0){
			pages.push(pagesTmp[i]);
		} else if(pagesTmp[i][3] != pagesTmp[i-1][3]){
			pages.push(pagesTmp[i]);
		}
	}

	// Concatinate all pages into one string 
	for(p of pages){
		//console.log(p[0] + "." + p[1] + "-" + p[2]);
		allPages += p[3];
	}

	// Open "save file" dialog
	try{
		if(allPages != ''){
			console.log("opening save file dialog ...");
			var tempElem = document.createElement('a');
		    tempElem.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(allPages));
		    tempElem.setAttribute('download', "filename");
		    tempElem.click();
		}
	} catch(err) {
		console.log(err);
	} 
}

function sortStepFunction(a, b) {
	aStep = parseInt(a[0]);
	bStep = parseInt(b[0]);
	aSubStep = parseInt(a[1]);
	bSubStep = parseInt(b[1]);
	aQuizNum = parseInt(a[2]);
	bQuizNum = parseInt(b[2]);
    if (aStep === bStep) {
    	if(aSubStep === bSubStep){
    		return aQuizNum - bQuizNum;
    	} else {
    		return aSubStep - bSubStep;
    	}
     }
     else {
        return aStep - bStep;
    }
}

