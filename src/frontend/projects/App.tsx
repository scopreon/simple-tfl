import './App.css';

type Project = {
  name: string;
  description: string;
  github: string;
  references?: {
    label: string;
    href: string;
  }[];
};

const projects: Project[] = [
  {
    name: 'Generic Compilation Database Generator',
    description:
      'Rust reimplementation of the C++ tool Bear for generating compilation databases \
      by intercepting Linux build processes. Uses LD_PRELOAD to hook syscalls and a \
      custom Unix Domain Socket server with Protobuf for the data layer.',
    github: 'https://github.com/scopreon/rust-bear',
    references: [
      {
        label: 'Bear',
        href: 'https://github.com/rizsotto/Bear',
      },
    ],
  },
  {
    name: 'TFL times',
    description:
      'I realised I would often arrive at Bank station to early for my train have have to \
      wait 10+ minutes. React frontend listening on Python server with websockets. Built \
      fully custom typed asyncio TTL caching infrastructure with full suite of tests.',
    github: 'https://github.com/scopreon/saul.sh',
    references: [
      {
        label: 'TFL App',
        href: 'https://saul.sh/tfl',
      },
      {
        label: 'Caching',
        href: 'https://github.com/scopreon/saul.sh/blob/main/src/backend/cache.py',
      },
    ],
  },
  {
    name: 'Dockerised React Website',
    description:
      'Production-ready React website containerised with Docker and backed by a CI/CD \
      pipeline using GitHub Actions on a self-hosted runner. CI executes automated tests \
      and deployment on merge with main.',
    github: 'https://github.com/scopreon/saul.sh',
  },
];

type ProjectCardProps = Project;

function ProjectCard({
  name,
  description,
  github,
  references,
}: ProjectCardProps) {
  return (
    <div className="project-card">
      <h2 className="project-title">{name}</h2>
      <p className="project-description">{description}</p>
      <a
        className="project-link"
        href={github}
        target="_blank"
        rel="noopener noreferrer"
      >
        View on GitHub →
      </a>
      {references && (
        <div className="project-references">
          {references.map((ref) => (
            <a
              key={ref.href}
              href={ref.href}
              target="_blank"
              rel="noopener noreferrer"
              className="project-ref-link"
            >
              {ref.label}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

export function App() {
  return (
    <>
      <h1 className="page-title">Projects</h1>
      <h2 className="page-sub-title">AI usage kept to bare minimum</h2>

      <div className="projects-grid">
        {projects.map((project) => (
          <ProjectCard key={project.name} {...project} />
        ))}
      </div>
    </>
  );
}
