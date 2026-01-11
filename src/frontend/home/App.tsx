import Canvas from './canvas';

export function App() {
  return (
    <>
      <h1>Welcome!!!</h1>
      <p> WebGL Mandelbrot (drag and scroll to zoom)</p>
      <br></br>
      <Canvas width={500} height={500} />
    </>
  );
}
