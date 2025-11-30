import Entry from './entry.tsx';
import './App.css';
import { useState, useEffect } from 'react';

interface TflData {
  destination: string;
  time: number;
}

function App() {
  const [state, setState] = useState<TflData[]>([]);

  useEffect(() => {
    const socket = new WebSocket(
      'ws://localhost:8001/ws/arrivals/bank/northern/outbound'
    );

    const socket2 = new WebSocket('ws://localhost:8001/ws/status/northern');

    socket2.addEventListener('message', (event) => {
      console.log(JSON.parse(event.data));
    });

    socket.addEventListener('message', (event) => {
      const arr: TflData[] = [];

      for (const line of event.data.split('\n')) {
        try {
          const parsed = JSON.parse(line);
          parsed.time = Math.floor(parsed.time / 60);
          arr.push(parsed);
        } catch (e) {
          console.warn('Bad JSON line:', line);
        }
      }

      arr.sort((data1, data2) => {
        return data1.time - data2.time;
      });
      setState(arr); // <-- update state here
    });

    return () => socket.close(); // cleanup
  }, []); // run once

  return (
    <div>
      {state.map((dest, i) => (
        <Entry key={i} destination={dest.destination} time={dest.time} />
      ))}
    </div>
  );
}

export default App;
