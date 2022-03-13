(function() {

    var login = null;
    var userName = null; 
    var wsConnection = null;
    var chat = null;
    var wsServerURL = "ws://192.168.4.22:8000/"; 
    var wsProtocols = "json";
    var clientID = 0;


    window.addEventListener('load', startup, false);

    function startup(){

        login = document.getElementById('login');
        chat = document.getElementById('chat');
        var chatbox = document.getElementById("chatbox").contentDocument;

        login.addEventListener('click', () => {
            
            
            userName = document.getElementById('name').value;

            // wsConnection = new WebSocket(wsServerURL, "json") ====> error? 
            wsConnection = new WebSocket(wsServerURL)

            console.log((new Date()) + ": WebSocket conneciton created, currently in " + wsConnection.readyState + " state.")
        

            //create event listener for 'open' to handle the newly established WS connection 
            wsConnection.addEventListener('open', () => {
                document.getElementById("text").disabled = false;
                document.getElementById("chat").disabled = false;
                console.log((new Date()) + ": WebSocket conneciton is open, currently in " + wsConnection.readyState + " state.")
                wsSend(userName,"username",wsConnection)
                //disable the login to avoid multiple connections to be established 
                document.getElementById("name").disabled = true;
                document.getElementById("login").disabled = true;
            } )


            //create event listener for 'message' to handle inbound WS messages
            wsConnection.addEventListener('message', (event) => {
                    console.log((new Date()) + ": " + event.data);
                    var msg = JSON.parse(event.data);
                    switch(msg.type){
                    case "chat-received":
                        var chattext = new Date().toLocaleTimeString() + " <b> " + msg.userName + "</b>: " + msg.data + "<br>";
                        chatbox.write(chattext);
                        console.log(chatbox)
                        break; 
                 }
                
            })

            //create event listener for send button and dispatch the chat text
            chat.addEventListener('click', () => {
                wsSend(document.getElementById("text").value, "chat-text", wsConnection);
                document.getElementById("text").value = "";
            })
            
        })
    }

    function wsSend(data, type, connection){

        var message = {
            data: data,
            type: type,
            id: clientID,
            date: Date.now(),
        }
        connection.send(JSON.stringify(message));
    }

    // function handleKey(evt) {
    //     if (evt.keyCode === 13 || evt.keyCode === 14) {
    //       if (!document.getElementById("send").disabled) {
    //         send();
    //       }
    //     }
    //   }

})();