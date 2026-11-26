type UserAccessGateProps = { onSignIn: () => void }

export default function UserAccessGate({ onSignIn }: UserAccessGateProps) {
  return <main className="admin-gate"><div className="admin-gate-card"><p className="eyebrow">STAYGRID ACCOUNT</p><h1>Your account</h1><p>Sign in to view your reservations, profile, and account summary.</p><button className="gold" onClick={onSignIn}>Sign in →</button></div></main>
}
