import Canvas from './canvas';
import './App.css';

export function App() {
  return (
    <div className="mandelbrot-page">
      <h1>Hi</h1>
      <p>WebGL Mandelbrot (drag and scroll to zoom)</p>
      <Canvas width={500} height={500} />
    </div>
  );
}
