import React, { useState, useEffect } from 'react';
import { socket } from '../socket';

function Game() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    function onChatMessage(data) {
      setMessages(prev => [...prev, `${data.sid}: ${data.message}`]);
    }
    socket.on('chat_message', onChatMessage);

    return () => {
      socket.off('chat_message', onChatMessage);
    }
  }, []);

  const handleSend = () => {
    if (input.trim()) {
      socket.emit('chat_message', { message: input });
      setInput('');
    }
  };

  return (
    <div>
      <h2>Game In Progress</h2>
      <div className="question-area">
        <p>This is where the quiz question will appear.</p>
      </div>
      <div className="chat-area">
        <h3>Live Chat</h3>
        <div className="messages">
          {messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}
        </div>
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default Game;

# Powered by Innovate CLI, a product of vaidik.co
