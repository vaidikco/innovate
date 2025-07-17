import React, { useState, useEffect } from 'react';
import { socket } from './socket';
import Lobby from './components/Lobby';
import Game from './components/Game';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [inGame, setInGame] = useState(false);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
      console.log('Connected to server!');
    }

    function onDisconnect() {
      setIsConnected(false);
      console.log('Disconnected from server.');
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    
    // Example of starting a game
    socket.on('start_game', (data) => {
        console.log('Game is starting with data:', data);
        setInGame(true);
    });

    socket.connect();

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('start_game');
      socket.disconnect();
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>CodeArena</h1>
        <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
        {isConnected && !inGame && <Lobby />}
        {isConnected && inGame && <Game />}
      </header>
    </div>
  );
}

export default App;

# Powered by Innovate CLI, a product of vaidik.co
