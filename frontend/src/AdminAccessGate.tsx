type AdminAccessGateProps = { onSignIn: () => void }

export default function AdminAccessGate({ onSignIn }: AdminAccessGateProps) {
  return <main className="admin-gate"><div className="admin-gate-card"><p className="eyebrow">STAYGRID ADMIN</p><h1>Admin dashboard</h1><p>Manage hotels, room inventory, reservations, and reports from the protected control centre.</p><button className="gold" onClick={onSignIn}>Sign in as administrator →</button><small>Admin access is restricted to accounts with the administrator role.</small></div></main>
}
