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
            } )


            //create event listener for 'message' to handle inbound WS messages
            wsConnection.addEventListener('message', (event) => {
                console.log(event.data);
            })


            //create event listener for send button and dispatch the chat message
            chat.addEventListener('click', () => {
                wsSend(document.getElementById("text").value,"message",wsConnection);
            })
            
        })
    }

    function wsSend(data, type, connection){

        var message = {
            text: data,
            type: type,
            id: clientID,
            date: Date.now(),
            misc: "idd message"
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