import { mat4 } from 'gl-matrix';
import { useRef, useEffect } from 'react';

type CanvasProps = {
  width: number;
  height: number;
};

// Vertex shader program
const vsSource = `
attribute vec4 aVertexPosition;
uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;
void main() {
  gl_Position = aVertexPosition;
}
`;

// Fragment shader program with zoom & offset
const fsSource = `
#ifdef GL_ES
precision highp float;
#endif

uniform vec2 u_resolution;
uniform float u_zoom;
uniform vec2 u_offset;

#define multiply_imaginary(vec_1, vec_2) vec2(vec_1.x * vec_2.x - vec_1.y * vec_2.y, vec_1.x * vec_2.y + vec_1.y * vec_2.x) 

vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(
        abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0,
        0.0,
        1.0
    );
    return c.z * mix(vec3(1.0), rgb, c.y);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution;
    st.x *= u_resolution.x / u_resolution.y;

    // Zoom & offset
    st -= 0.5;
    st /= u_zoom;
    st += u_offset;

    // st.x *= 5.0;
    // st.y *= 5.0;

    vec2 initial = st;
    int rate = 0;
    for(int i = 0; i < 256; i++){
        initial = multiply_imaginary(initial, initial) + st;
        float radius = sqrt(initial.x * initial.x + initial.y * initial.y);
        if(radius > 2.0){
          rate = i;
          break;
        }
    }
    float t = float(rate) / 256.0;   // normalize iterations
    float hue = t;                  // hue ∈ [0,1)
    float saturation = 1.0;
    float value = rate == 0 ? 0.0 : 1.0;  // inside set = black

    vec3 color = hsv2rgb(vec3(hue, saturation, value));
    gl_FragColor = vec4(color, 1.0);
}
`;

function initShaderProgram(
  gl: WebGLRenderingContext,
  vsSource: string,
  fsSource: string
) {
  const vertexShader = loadShader(gl, gl.VERTEX_SHADER, vsSource);
  const fragmentShader = loadShader(gl, gl.FRAGMENT_SHADER, fsSource);
  if (!vertexShader || !fragmentShader) return null;

  const shaderProgram = gl.createProgram();
  if (!shaderProgram) return null;

  gl.attachShader(shaderProgram, vertexShader);
  gl.attachShader(shaderProgram, fragmentShader);
  gl.linkProgram(shaderProgram);

  if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
    console.error(
      'Unable to initialize shader program:',
      gl.getProgramInfoLog(shaderProgram)
    );
    return null;
  }
  return shaderProgram;
}

function loadShader(gl: WebGLRenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) return null;

  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error('Error compiling shader:', gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

function initPositionBuffer(gl: WebGLRenderingContext) {
  const positionBuffer = gl.createBuffer();
  if (!positionBuffer) return null;

  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  const positions = [1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0];
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
  return positionBuffer;
}

function setPositionAttribute(
  gl: WebGLRenderingContext,
  buffers: { position: WebGLBuffer | null },
  programInfo: any
) {
  gl.bindBuffer(gl.ARRAY_BUFFER, buffers.position);
  gl.vertexAttribPointer(
    programInfo.attribLocations.vertexPosition,
    2,
    gl.FLOAT,
    false,
    0,
    0
  );
  gl.enableVertexAttribArray(programInfo.attribLocations.vertexPosition);
}

function drawScene(
  gl: WebGLRenderingContext,
  programInfo: any,
  buffers: { position: WebGLBuffer | null },
  zoom: number,
  offset: { x: number; y: number }
) {
  gl.clearColor(0, 0, 0, 1);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  const fieldOfView = (45 * Math.PI) / 180;
  const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;
  const projectionMatrix = mat4.create();
  mat4.perspective(projectionMatrix, fieldOfView, aspect, 0.1, 100.0);

  const modelViewMatrix = mat4.create();
  mat4.translate(modelViewMatrix, modelViewMatrix, [-0.0, 0.0, -6.0]);

  setPositionAttribute(gl, buffers, programInfo);
  gl.useProgram(programInfo.program);

  gl.uniformMatrix4fv(
    programInfo.uniformLocations.projectionMatrix,
    false,
    projectionMatrix
  );
  gl.uniformMatrix4fv(
    programInfo.uniformLocations.modelViewMatrix,
    false,
    modelViewMatrix
  );
  gl.uniform2f(
    programInfo.uniformLocations.resolution,
    gl.canvas.width,
    gl.canvas.height
  );
  gl.uniform1f(programInfo.uniformLocations.zoom, zoom);
  gl.uniform2f(programInfo.uniformLocations.offset, offset.x, offset.y);

  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
}

export default function Canvas({ width, height }: CanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const zoomRef = useRef(0.25);
  const offsetRef = useRef({ x: -0.5, y: 0 });
  const isDragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const gl = canvas.getContext('webgl');
    if (!gl) return;

    const shaderProgram = initShaderProgram(gl, vsSource, fsSource);
    if (!shaderProgram) return;

    const programInfo = {
      program: shaderProgram,
      attribLocations: {
        vertexPosition: gl.getAttribLocation(shaderProgram, 'aVertexPosition'),
      },
      uniformLocations: {
        projectionMatrix: gl.getUniformLocation(
          shaderProgram,
          'uProjectionMatrix'
        ),
        modelViewMatrix: gl.getUniformLocation(
          shaderProgram,
          'uModelViewMatrix'
        ),
        resolution: gl.getUniformLocation(shaderProgram, 'u_resolution'),
        zoom: gl.getUniformLocation(shaderProgram, 'u_zoom'),
        offset: gl.getUniformLocation(shaderProgram, 'u_offset'),
      },
    };

    const buffers = { position: initPositionBuffer(gl) };
    if (!buffers.position) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    gl.viewport(0, 0, canvas.width, canvas.height);

    // Draw initial scene
    drawScene(gl, programInfo, buffers, zoomRef.current, offsetRef.current);

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();

      const rect = canvas.getBoundingClientRect();

      // Mouse position in pixel coordinates
      let mouseX = e.clientX - rect.left;
      let mouseY = e.clientY - rect.top;
      console.log(e.clientX, rect.left, canvas.width);

      // Convert to normalized coordinates [-0.5, 0.5]
      let nx = mouseX / rect.width - 0.5;
      let ny = 0.5 - mouseY / rect.height; // flip Y

      // // Apply aspect ratio
      // nx *= canvas.width / canvas.height;

      const zoomFactor = Math.exp(-e.deltaY * 0.001);

      // Adjust offset so point under mouse stays fixed
      // offsetRef.current.x =
      //   offsetRef.current.x + (nx * (1 - 1 / zoomFactor)) / zoomRef.current;
      // offsetRef.current.y =
      //   offsetRef.current.y + (ny * (1 - 1 / zoomFactor)) / zoomRef.current;
      offsetRef.current.x =
        nx / zoomRef.current -
        nx / (zoomRef.current * zoomFactor) +
        offsetRef.current.x;
      offsetRef.current.y =
        ny / zoomRef.current -
        ny / (zoomRef.current * zoomFactor) +
        offsetRef.current.y;
      // console.log(offsetRef.current);
      console.log(nx, ny);
      // Update zoom
      zoomRef.current *= zoomFactor;

      drawScene(gl!, programInfo, buffers, zoomRef.current, offsetRef.current);
    };

    canvas.addEventListener('wheel', handleWheel);

    // Drag to pan
    const handleMouseDown = (e: MouseEvent) => {
      isDragging.current = true;
      lastMouse.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
      isDragging.current = false;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;
      const dx = (e.clientX - lastMouse.current.x) / canvas.width;
      const dy = (e.clientY - lastMouse.current.y) / canvas.height;
      offsetRef.current.x -=
        ((dx * (canvas.width / canvas.height)) / zoomRef.current) * 2;
      offsetRef.current.y += (dy / zoomRef.current) * 2;
      lastMouse.current = { x: e.clientX, y: e.clientY };

      console.log(offsetRef.current);
      drawScene(gl, programInfo, buffers, zoomRef.current, offsetRef.current);
    };

    canvas.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mousemove', handleMouseMove);

    return () => {
      // canvas.removeEventListener('wheel', handleWheel);
      canvas.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, [width, height]);

  return <canvas ref={canvasRef} />;
}
