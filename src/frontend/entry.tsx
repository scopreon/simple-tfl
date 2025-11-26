export default function Entry({
  destination,
  time = 0,
}: {
  destination: string;
  time?: number;
}) {
  return (
    <div className="tflEntry">
      <p>{destination}</p>
      <span>{time.toString()} mins</span>
    </div>
  );
}
