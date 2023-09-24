var xmlHttp = createXmlHttpRequestObject();
var temperature = 90
var jsontotal = 0
handleServerResponse();


function createXmlHttpRequestObject(){
	var xmlHttp;
	
	if(window.ActiveXObject){
		try{
			xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
		}catch(e){
			xmlHttp = false;
		}
	}else{
		try{
			xmlHttp = new XMLHttpRequest();
		}catch(e){
			xmlHttp = false;
		}
	}
	
	if (!xmlHttp){
		alert("can't creat the object")
	}else{
		return xmlHttp;
	}
}

function toggle(ids) {
    e = document.getElementById(ids.id);
    if (ids.id == "OnOff") {
        if (ids.value == "LIGHTS ON") {
            ids.value = "LIGHTS OFF";
            e.style.backgroundColor = "rgb(40,100,40)";
            xmlHttp.open("POST", "../cgi-bin/LCpi1.py", true);
            xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xmlHttp.onreadystatechange = handleServerResponse;
            xmlHttp.send("LawnConnect_Off=Ready");
        } else {
            ids.value = "LIGHTS ON";
            e.style.backgroundColor = "rgb(20,150,50)";
            xmlHttp.open("POST", "../cgi-bin/LCpi1.py", true);
            xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xmlHttp.onreadystatechange = handleServerResponse;
            xmlHttp.send("LawnConnect_On=Ready");
        }
    }
    // CAlibrate button is not a toggle so, I need to check for it in the next two if statements
    if (ids.id == "Calibrate"){
        if (ids.value == "CALIBRATE") {
            ids.value = "CALIBRATING";
            e.style.backgroundColor = "rgb(20,150,50)";
            xmlHttp.open("POST", "../cgi-bin/LCpi1.py", true);
            xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xmlHttp.onreadystatechange = handleServerResponse;
            xmlHttp.send("Calibrate_On=Ready");
        }
    }
    
}


function process(){
	//alert("inside process")
	if(xmlHttp.readyState==0 || xmlHttp.readyState==4){
		//food = encodeURIComponent(document.getElementById("userInput").value);
		xmlHttp.open("GET", "../cgi-bin/LCpi1.py", true);
		xmlHttp.onreadystatechange = handleServerResponse;
		xmlHttp.send(null);
	}
    //else{
	//	setTimeout('process()',100);
	//}
}



function handleServerResponse(){
	//alert("inside the handleserverresponse")
	if(xmlHttp.readyState==4){
		if(xmlHttp.status==200){
			//alert("looking for server request")
			xmlResponse = xmlHttp.responseText;
                        jsontotal = JSON.parse(xmlResponse);
			document.getElementById("next_turn_on").innerHTML = jsontotal.NextTurnOn;
   			document.getElementById("next_turn_off").innerHTML = jsontotal.NextTurnOff;
    			document.getElementById("current").innerHTML = jsontotal.PeakRead;
			if(jsontotal.LC_ON){
				//alert("LC_ON is true")
				document.getElementById("OnOff").value = "LIGHTS ON"
				document.getElementById("OnOff").style.backgroundColor = "rgb(20,150,50)"
			}else{
				document.getElementById("OnOff").value = "LIGHTS OFF"
				document.getElementById("OnOff").style.backgroundColor = "rgb(40,100,40)"
			}
            if(jsontotal.LampOff){
				//alert("LC_ON is true")
				document.getElementById("LampOff").innerHTML = "LAMP BURNT OUT"
			}else{
				document.getElementById("LampOff").innerHTML = ""
			}
			if(jsontotal.LampCalibrate){
				//alert("Calibrate is true")
				//document.getElementById("Calibrate").value = "CALIBRATING"
				//document.getElementById("Calibrate").style.backgroundColor = "rgb(20,150,50)"
			}else{
				document.getElementById("Calibrate").value = "CALIBRATE"
				document.getElementById("Calibrate").style.backgroundColor = "rgb(40,100,40)"
			}
			
			//setTimeout('process()',100);	
			//alert("after timeout")	
		}else{
			//alert('Something went wrong!')
		}
	}
    else{
		//alert("not readystate 4")
		setTimeout('process()',100)
	}
}



	  
	  
	  
	  
	  
