let correctFeedbackSet = new Set();
let incorrectFeedbackSet = new Set();
let correctAnswerSet = new Set();
let allAnswerIdSet = new Set();

function extractQuiz(urlRoot, node){
	// make sure sets are empty to begin with
	correctFeedbackSet = new Set();
	incorrectFeedbackSet = new Set();
	correctAnswerSet = new Set();
	allAnswerIdSet = new Set();

	// Get question text
	var questionTuple = extractQuestion(node);
	var questionText = questionTuple[1];
	//var questionText = questionTuple[0] + "\n" + questionTuple[1];
	//console.log(questionText);

	// Get correct answer
	var answerText = extractAnswer(urlRoot, node);
	//console.log(answerText);

	// Get feedback text
	var feedbackText = extractFeedback(urlRoot, node);
	//console.log(feedbackText);

	var quizText = questionText + answerText + feedbackText;
	return [questionTuple[0], quizText];
	
}

function extractQuestion(node){
	var quizText = '';
	var quizNum = 0;
	var quizHeadEl = node.getElementsByClassName("quizitem_header");
	if(quizHeadEl.length == 1){
		tmp = trimNewlines(quizHeadEl[0].textContent);
		quizText += tmp + "\n";
		quizNum = parseInt(tmp.split(" ")[1]);
	}
	var quizQuesEl = node.getElementsByClassName("quizitem_question");
	for(q of quizQuesEl){
		quizText += trimNewlines(q.textContent) + "\n";
	}
	var quizAnsEl = node.getElementsByClassName("quizitem_optiontext")
	for(q of quizAnsEl){
		quizText += trimNewlines(q.textContent) + "\n";
	}
	return [quizNum, quizText];
}

function extractAnswer(urlRoot, node){
	httpGetAnswerReveal(urlRoot);
	var answerText = "---\nCorrect answer(s):\n";
	for(ca of correctAnswerSet){
		answerText += trimNewlines(ca) + "\n";
	}
	return answerText;
}

function extractFeedback(urlRoot, node){
	// Get auth token
	var authToken = "";
	var form = node.getElementsByClassName("quizitem")[0];
	var auths = form.querySelectorAll('[name="authenticity_token"]');
	if(auths.length == 1){
		authToken = auths[0].value;
	} else { return ""; }

	// Get answer IDs
	var ansIds = [];
	var els = node.querySelectorAll('[name="multiple_choice_response[answer_ids][]"]');
	if (els.length == 0) {
		els = node.querySelectorAll('[name="quiz_response[answer_ids][]"]');
	}
	for (el of els) {
		ansIds.push(el.value);
	}

	// Check whether each answer is correct
	for(ansId of ansIds){
		httpPostFeedback(urlRoot, authToken, ansId);
	}

	// If question had a single answer it will have already been found 
	// If the answer hasn't already been found, look at getting close answers and feedback
	if(correctAnswerSet.size == 0){
		var clozeEls = node.querySelectorAll('[name="cloze_response[answers][]"]');
		// Get close answer questioins
		if(clozeEls.length > 0){
			httpPostClozeFeedback(urlRoot, node);
		} 
	}

	// Format feedback text
	var feedbackText = "";
	for(cf of correctFeedbackSet){
		feedbackText += "---\nFeedback correct:\n" + trimNewlines(cf) + "\n";
	}
	for(icf of incorrectFeedbackSet){
		feedbackText += "---\nFeedback incorrect:\n" + trimNewlines(icf) + "\n";
	}
	return feedbackText;
}

function httpGetAnswerReveal(urlRoot){

	console.log("formatting: sending get request for correct answer");

	var http = new XMLHttpRequest();
	var url = urlRoot + "/reveal";
	http.open("GET", url, false);
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	http.onreadystatechange = function() {
	    if(http.readyState == 4 && http.status == 200) {
			var respDoc = document.createElement('div');
			respDoc.innerHTML = http.responseText;
			var els = respDoc.getElementsByClassName("quizitem_correct_answer");
			// Get all possible correct answers (i.e. multiple choice and single choice)
			for(el of els){
				if(correctAnswerSet.has(el.textContent) != true){
					correctAnswerSet.add(el.textContent);
				}
			}
			var elsCloze = respDoc.querySelectorAll('[name="cloze_response[answers][]"]');
			for(elCloze of elsCloze){
				if(correctAnswerSet.has(elCloze.value) != true){
					correctAnswerSet.add(elCloze.value);
				}
			}
			// Get feedback for correct answer
			if(respDoc.getElementsByClassName("quizitem_feedback_text").length > 0){
				var feedbackText = respDoc.getElementsByClassName("quizitem_feedback_text")[0].textContent;
				if(correctFeedbackSet.has(feedbackText) != true){
					correctFeedbackSet.add(feedbackText);
				}
			}
	    }
	}
	http.send();
}

function httpPostClozeFeedback(urlRoot, node){
	// Get auth token
	var authToken = "";
	var form = node.getElementsByClassName("new_cloze_response")[0];
	var auths = form.querySelectorAll('[name="authenticity_token"]');
	if(auths.length == 1){
		authToken = auths[0].value;
	} else { return ""; }

	try{
		console.log("formatting: sending post request for cloze answer");
		var values = "utf8=✓&_method=put&cloze_response[answers][]=abcd&authenticity_token=" + encodeURIComponent(authToken);
		var http = new XMLHttpRequest();
		var url = urlRoot;
		var params = values;
		http.open("POST", url, false);
		http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

		http.onreadystatechange = function() {
		    if(http.readyState == 4 && http.status == 200) {
				var respDoc = document.createElement('div');
				respDoc.innerHTML = http.responseText;	
				if(respDoc.getElementsByClassName("quizitem_feedback_text").length > 0){
					var feedbackText = respDoc.getElementsByClassName("quizitem_feedback_text")[0].textContent;
					if(incorrectFeedbackSet.has(feedbackText) != true){
						incorrectFeedbackSet.add(feedbackText);
					}
				}	
			}
		}
		http.send(params);
	} catch(err) {
		console.log(err);
	} 
}

function httpPostFeedback(urlRoot, authToken, ansId){	
	try{
		if(allAnswerIdSet.has(ansId) != true){
			console.log("formatting: sending post request for feedback on answer " + ansId);
			var values = "utf8=✓&_method=put&multiple_choice_response[answer_ids][]=" + ansId + "&authenticity_token=" + encodeURIComponent(authToken);
			allAnswerIdSet.add(ansId);
			var http = new XMLHttpRequest();
			var url = urlRoot;
			var params = values;
			http.open("POST", url, false);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

			http.onreadystatechange = function() {
			    if(http.readyState == 4 && http.status == 200) {
					var respDoc = document.createElement('div');
					respDoc.innerHTML = http.responseText;
					var correctFeedback = false; 
					if(respDoc.getElementsByClassName("quizitem_correct_answer").length > 0){
						correctFeedback = true;
						var ansArr = respDoc.getElementsByClassName("quizitem_correct_answer");
						for (ans of ansArr){
							if(correctAnswerSet.has(ans.textContent) != true){
								correctAnswerSet.add(ans.textContent);
							}
						}
					}
					if(respDoc.getElementsByClassName("quizitem_result-incorrect").length > 0){
						correctFeedback = false;
					}	
					if(respDoc.getElementsByClassName("quizitem_feedback_text").length > 0){
						var feedbackText = respDoc.getElementsByClassName("quizitem_feedback_text")[0].textContent;
						if(correctFeedback){
							if(correctFeedbackSet.has(feedbackText) != true){
								correctFeedbackSet.add(feedbackText);
							}
						} else {
							if(incorrectFeedbackSet.has(feedbackText) != true){
								incorrectFeedbackSet.add(feedbackText);
							}
						}
					}		
			    }
			}
			http.send(params);
		}
	} catch(err) {
		console.log(err);
	} 
}

