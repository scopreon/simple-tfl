import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { App as TFLApp } from './tfl/App.tsx';
import { App as HomeApp } from './home/App.tsx';
import { App as ProjectsApp } from './projects/App.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      {/* Navigation */}
      <nav>
        <Link to="/">Home</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/tfl">TFL</Link>
      </nav>

      {/* Routes */}
      <Routes>
        <Route path="/" element={<HomeApp />} />
        <Route path="/projects" element={<ProjectsApp />} />
        <Route path="/tfl" element={<TFLApp />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
