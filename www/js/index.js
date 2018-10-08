var deviceTime = document.querySelector('.status-bar .time');
var messageTime = document.querySelectorAll('.message .time');
deviceTime.innerHTML = moment().format('H:mm');
setInterval(function() {
    deviceTime.innerHTML = moment().format('H:mm');
}, 1000);
for (var i = 0; i < messageTime.length; i++) {
    messageTime[i].innerHTML = moment().format('H:mm');
}

var form = document.querySelector('.conversation-compose');
var conversation = document.querySelector('.conversation-container');

form.addEventListener('submit', newMessage);

function wpp_regex(text) {
    return text.replace(/\*([^*]*)\*/g, '&zwnj;<b style="color:#000000;">$1</b>&zwnj;').replace(/&zwnj;<b style="color:#000000;"><\/b>&zwnj;/g, '**').replace(/_([^_]*)_/g, '&zwnj;<i>$1</i>&zwnj;').replace(/&zwnj;<i><\/i>&zwnj;/g, '__').replace(/~([^~]*)~/g, '&zwnj;<s>$1</s>&zwnj;').replace(/&zwnj;<s><\/s>&zwnj;/g, '~~').replace(/```([^```]*)```/g, '&zwnj;<mono>$1</mono>&zwnj;').replace(/zwnj;<mono><\/mono>&zwnj;/g, '``````');
}


function UserAction(url) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
    return JSON.parse(xhttp.responseText);
}

function Get(yourUrl) {
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET", yourUrl, false);
    Httpreq.send(null);
    return Httpreq.responseText;
}

function toUnicode(str) {
    return str.split('').map(function(value, index, array) {
        var temp = value.charCodeAt(0).toString(16).toUpperCase();
        if (temp.length > 2) {
            return '\\u' + temp;
        }
        return value;
    }).join('');
}


function fake_terminal_get(g_section, send, g_input, g_retry, g_record) {
    var currentdate = new Date();
    var datetime = "[" + currentdate.getDate() + "/" + (currentdate.getMonth() + 1) + "/" + currentdate.getFullYear() + " " + currentdate.getHours() + ":" + currentdate.getMinutes() + ":" + currentdate.getSeconds() + "]";
    var elem = document.getElementById('terminal');
    elem.innerHTML += '<p>GET ' + datetime + ' "/chatbot-demo/api/v1/section=' + g_section + '&message=' + encodeURI(send) + '&input_value=' + g_input + '&retry=' + g_retry + '&record=' + g_record + '"</p>';
    elem.scrollTop = elem.scrollHeight;

}


function fake_terminal_return(g_section, g_message, g_input, g_retry, g_record) {
    if (g_message == "") {
        g_message = "null";
    } else {
        g_message = '"' + toUnicode(g_message) + '"';
    }
    var elem = document.getElementById('terminal');
    elem.innerHTML += '<p>RETURN {"section": ' + g_section + ', "message": ' + g_message + ', "input_value": ' + g_input + ', "retry": ' + g_retry + ', "record": "' + g_record + '"}</p>';
    elem.scrollTop = elem.scrollHeight;
}


function newMessage(e) {

    var input = e.target.input;
    var send = input.value.replace(/\//g, '-');
    days = 30;
    myDate = new Date();
    myDate.setTime(myDate.getTime() + (days * 24 * 60 * 60 * 1000));
    var calljson = './vendor/external.php?section=' + g_section + '&message=' + send + '&input_value=' + g_input + '&retry=' + g_retry + '&record=' + g_record + ''
    fake_terminal_get(g_section, input.value, g_input, g_retry, g_record);
    var json_obj = JSON.parse(Get(encodeURI(calljson)));
    g_section = json_obj.section;
    g_record = json_obj.record;
    g_retry = json_obj.retry;
    g_input = json_obj.input;
    g_message = json_obj.message;
    prev_g_section = g_section;
    prev_g_input = g_input;




    if ((g_message == "")) {
        calljson = './vendor/external.php?section=' + g_section + '&message=null&input_value=' + g_input + '&retry=' + g_retry + '&record=' + g_record + ''

        json_obj = JSON.parse(Get(encodeURI(calljson)));
        g_section = json_obj.section;
        g_record = json_obj.record;
        g_retry = json_obj.retry;
        g_input = json_obj.input;
        g_message = json_obj.message;

    }
    fake_terminal_return(g_section, g_message, g_input, g_retry, g_record);
    g_message = wpp_regex(g_message).replace(/\n/g, "<br>");


    if (input.value) {
        var message = buildMessage(input.value, 1);
        conversation.appendChild(message);
        animateMessage(message);

        var message = buildMessage(g_message, 0);
        conversation.appendChild(message);
        animateMessage(message);
        while (g_retry == 1) {
            prev_g_section = g_section;
            calljson = './vendor/external.php?section=' + g_section + '&message=null&input_value=' + g_input + '&retry=' + g_retry + '&record=' + g_record + ''
            json_obj = JSON.parse(Get(encodeURI(calljson)));

            g_section = json_obj.section;
            g_record = json_obj.record;
            g_retry = json_obj.retry;
            g_input = json_obj.input;
            g_message = json_obj.message;

            fake_terminal_return(g_section, g_message, g_input, g_retry, g_record);

            g_message = wpp_regex(g_message).replace(/\n/g, "<br>");
            var message = buildMessage(g_message, 0);
            conversation.appendChild(message);
            animateMessage(message);
        }
    }

    input.value = '';
    conversation.scrollTop = conversation.scrollHeight;

    e.preventDefault();
}

function buildMessage(text, type) {
    var element = document.createElement('div');

    if (type == 1) {
        element.classList.add('message', 'sent');
    } else {
        element.classList.add('message', 'received');
    }

    element.innerHTML = text +
        '<span class="metadata">' +
        '<span class="time">' + moment().format('H:mm') + '</span>' +
        '<span class="tick tick-animation">' +
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" id="msg-dblcheck" x="2047" y="2061"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.88a.32.32 0 0 1-.484.032l-.358-.325a.32.32 0 0 0-.484.032l-.378.48a.418.418 0 0 0 .036.54l1.32 1.267a.32.32 0 0 0 .484-.034l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.88a.32.32 0 0 1-.484.032L1.892 7.77a.366.366 0 0 0-.516.005l-.423.433a.364.364 0 0 0 .006.514l3.255 3.185a.32.32 0 0 0 .484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" fill="#92a58c"/></svg>' +
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" id="msg-dblcheck-ack" x="2063" y="2076"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.88a.32.32 0 0 1-.484.032l-.358-.325a.32.32 0 0 0-.484.032l-.378.48a.418.418 0 0 0 .036.54l1.32 1.267a.32.32 0 0 0 .484-.034l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.88a.32.32 0 0 1-.484.032L1.892 7.77a.366.366 0 0 0-.516.005l-.423.433a.364.364 0 0 0 .006.514l3.255 3.185a.32.32 0 0 0 .484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" fill="#4fc3f7"/></svg>' +
        '</span>' +
        '</span>';

    return element;
}

function animateMessage(message) {
    setTimeout(function() {
        var tick = message.querySelector('.tick');
        tick.classList.remove('tick-animation');
    }, 500);
}

function clearconsole() {
    var elem = document.getElementById('terminal');
    elem.innerHTML = '<p> { "start_simulation": true } </p>';
}

function clearchat() {
    g_section = '0';
    g_record = 'fHx8';
    g_retry = '0';
    g_input = '0';
    var elem = document.getElementById('chatbox');
    elem.innerHTML = null;
}
