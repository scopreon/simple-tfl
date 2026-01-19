import Entry from './entry.tsx';
import './App.css';
import { useState, useEffect } from 'react';

interface TflData {
  destination: string;
  time: number;
}

interface LineData {
  status: string;
  description: string;
}

export function App() {
  const [arrivals, setArrivals] = useState<TflData[]>([]);
  const [lineInfo, setLineInfo] = useState<LineData>({
    status: 'LOADING',
    description: 'LOADING',
  });

  useEffect(() => {
    const date = new Date();
    let start_station = '';
    let direction = '';
    if (date.getHours() < 12) {
      start_station = 'edgware';
      direction = 'inbound';
    } else {
      start_station = 'bank';
      direction = 'outbound';
    }
    const arrivalsSocket = new WebSocket(
      `/ws/arrivals/${start_station}/northern/${direction}`
    );

    const statusSocket = new WebSocket('/ws/status/northern');

    statusSocket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      setLineInfo({ status: data.status, description: data.description });
    });

    arrivalsSocket.addEventListener('message', (event) => {
      const arrivalsArr: TflData[] = [];

      for (const lineStr of event.data.split('\n')) {
        try {
          const parsed: TflData = JSON.parse(lineStr);
          console.log(parsed);
          parsed.time = Math.floor(parsed.time / 60);
          arrivalsArr.push(parsed);
        } catch (e) {
          console.warn('Bad JSON line:', lineStr);
        }
      }

      arrivalsArr.sort((data1, data2) => {
        return data1.time - data2.time;
      });
      setArrivals(arrivalsArr); // <-- update state here
    });

    return () => {
      arrivalsSocket.close();
      statusSocket.close();
    }; // cleanup
  }, []); // run once

  return (
    <>
      <div>
        <span>{lineInfo.status}</span>
        <p>{lineInfo.description}</p>
      </div>
      <div>
        {arrivals.map((arrival, i) => (
          <Entry
            key={i}
            destination={arrival.destination}
            time={arrival.time}
          />
        ))}
      </div>
    </>
  );
}
