document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var uploadMessage = document.getElementById('upload-message');
    var tableDisplay = document.getElementById('table-container');
    var tableDisplayHeading = document.getElementById('table-display-heading');
    var chatbox = document.getElementById('chatbox');
    var userMessageInput = document.getElementById('user-message');
    var clearButton = document.getElementById('clear-button');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        var summaryDiv = document.getElementById('summary');
        summaryDiv.innerHTML = '';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadMessage.textContent = data.message;
            if (data.table_html) {
                tableDisplayHeading.innerHTML = "Table Display";
                tableDisplay.innerHTML = data.table_html;
            }
            if (data.columns && data.rows) {
                var summaryDiv = document.getElementById('summary');
                var summaryHeading = document.getElementById('summary-heading');
                summaryHeading.innerHTML = '<h2>Summary</h2>';

                if (typeof data.missing === 'string') {
                    var summaryList = document.createElement('ul');
                    summaryList.innerHTML += '<li><b>Columns: </b>' + data.columns.join(', ') + '</li>';
                    summaryList.innerHTML += '<li><b>Number of Rolumns : </b>' + data.num_columns + '</li>';
                    summaryList.innerHTML += '<li><b>Rows: </b>' + data.rows + '</li>';
                    summaryList.innerHTML += '<li><b>Missing values: </b></li>';
                    var missingMessage = document.createElement('p');
                    missingMessage.textContent = data.missing;
                    summaryList.appendChild(missingMessage);
                    summaryDiv.appendChild(summaryList);
                } else {
                    var summaryList = document.createElement('ul');
                    summaryList.innerHTML += '<li><b>Column Names: </b>' + data.columns.join(', ') + '</li>';
                    summaryList.innerHTML += '<li><b>Number of Rolumns : </b>' + data.num_columns + '</li>';
                    summaryList.innerHTML += '<li><b>Number of Rows: </b>' + data.rows + '</li>';
                    summaryList.innerHTML += '<li><b>Missing values: </b></li>';
                    var missingList = document.createElement('ul');
                    for (var key in data.missing) {
                        missingList.innerHTML += '<li>' + key + ': ' + data.missing[key] + '</li>';
                    }
                    summaryList.appendChild(missingList);
                    summaryDiv.appendChild(summaryList);
                }

                summaryDiv.style.maxHeight = '30%';
                summaryDiv.style.overflowY = 'auto';
            }
        })

        .catch(error => console.error('Error:', error));
    });

    clearButton.addEventListener('click', function() {
        chatbox.innerHTML = '';
    });

    document.getElementById('send-button').addEventListener('click', function() {
        var userMessage = userMessageInput.value.trim();
        if (userMessage !== '') {
            displayUserMessage(userMessage);
            userMessageInput.value = '';
            sendUserMessage(userMessage);
        }
    });

    function displayUserMessage(message) {
        var userBubble = document.createElement('div');
        userBubble.classList.add('user-bubble');
        userBubble.textContent = message;
        chatbox.appendChild(userBubble);
        chatbox.appendChild(document.createElement('br'));
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function displayChatbotResponse(response) {
        var chatbotBubble = document.createElement('div');
    chatbotBubble.classList.add('chatbot-bubble');
    var lines = response.split('\n');
    lines.forEach(function(line) {
        var cleanedLine = line.replace(/[\[\]{}"]/g, ''); 
        var splitLine = cleanedLine.split(',');
        var newLine = splitLine.reduce(function(result, item, index) {
            result.push(item);
            if ((index + 1) % 2 === 0) {
                result.push('<br>'); 
            }
            return result;
        }, []).join('');
        var paragraph = document.createElement('p');
        paragraph.innerHTML = newLine;
        chatbotBubble.appendChild(paragraph);
    });
    chatbox.appendChild(chatbotBubble);
    chatbox.appendChild(document.createElement('br'));
    chatbox.scrollTop = chatbox.scrollHeight;
        if (response) {
            var visualizeHeading = document.getElementById('visualize-heading');
            visualizeHeading.innerHTML = '<h2>Visualize</h2>';
            var visualizeDiv = document.getElementById('visualize');
            var timestamp = new Date().getTime(); 
            var image = document.createElement('img');
            image.src = `${response}?t=${timestamp}`;
            image.alt = 'Plot';
            image.classList.add('visualize-image');
            visualizeDiv.innerHTML = '';
            visualizeDiv.appendChild(image);
        }
    }
    
    
    function sendUserMessage(message) {
        fetch('/process_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            displayChatbotResponse(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            displayChatbotResponse("Terri did not catch that, please try again.");
        });
    }
});
