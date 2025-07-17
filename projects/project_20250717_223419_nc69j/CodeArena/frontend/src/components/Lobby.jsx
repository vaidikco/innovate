import React from 'react';
import { socket } from '../socket';

function Lobby() {
  const handleFindMatch = () => {
    console.log('Finding match...');
    // This would be replaced with actual matchmaking logic
    // For now, we simulate a game start
    socket.emit('find_match', { skill: 'intermediate' });
  };

  return (
    <div>
      <h2>Matchmaking Lobby</h2>
      <button onClick={handleFindMatch}>Find Match</button>
    </div>
  );
}

export default Lobby;

# Powered by Innovate CLI, a product of vaidik.co
