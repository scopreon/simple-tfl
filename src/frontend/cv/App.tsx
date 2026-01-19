export function App() {
  return (
    <iframe
      src={`${import.meta.env.BASE_URL}cv/Saul_Cooperman_CV.pdf`}
      style={{ flex: 1, width: '100%', border: 'none' }}
      title="CV"
    />
  );
}
