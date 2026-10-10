export default function Placeholder({
  title,
  sprint,
  text,
}: {
  title: string
  sprint: string
  text: string
}) {
  return (
    <div className="page">
      <h1>{title}</h1>
      <div className="card placeholder">
        <span className="tag">{sprint}</span>
        <p>{text}</p>
      </div>
    </div>
  )
}
