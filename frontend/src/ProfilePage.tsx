type ProfileProps = { user: { name?: string; email?: string; role?: string } | null; onBookings: () => void; onSignOut: () => void }

export default function ProfilePage({ user, onBookings, onSignOut }: ProfileProps) {
  return <main className="content page profile-page">
    <p className="eyebrow">YOUR STAYGRID ACCOUNT</p>
    <h1>My profile</h1>
    <section className="profile-card">
      <div className="profile-avatar">{user?.name?.[0]?.toUpperCase() || '?'}</div>
      <div className="profile-details">
        <span className="profile-role">{user?.role === 'admin' ? 'ADMINISTRATOR' : 'CUSTOMER'}</span>
        <h2>{user?.name}</h2>
        <p>{user?.email}</p>
        <div className="profile-actions"><button className="gold" onClick={onBookings}>View my bookings</button><button className="outline" onClick={onSignOut}>Sign out</button></div>
      </div>
    </section>
    <div className="profile-info-grid"><div><span>Account access</span><b>{user?.role === 'admin' ? 'Administrator tools enabled' : 'Guest booking access'}</b></div><div><span>Member since</span><b>StayGrid member</b></div></div>
  </main>
}
