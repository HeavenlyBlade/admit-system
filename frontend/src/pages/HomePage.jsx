/**
 * HomePage - Primary landing page for ADMIT
 */
import TransitionLink from '../components/TransitionLink';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { user, login, isAuthenticated } = useAuth();

  const quickInfoCards = [
    {
      icon: '📋',
      title: 'Admission Requirements',
      desc: 'Learn what documents and qualifications you need to enroll at SACLI.',
    },
    {
      icon: '📝',
      title: 'Enrollment Steps',
      desc: 'Step-by-step guide through the SACLI enrollment process.',
    },
    {
      icon: '🎓',
      title: 'Scholarships',
      desc: 'Discover available scholarship programs and financial assistance options.',
    },
    {
      icon: '📞',
      title: 'Contact & Support',
      desc: 'Get in touch with the SACLI admissions office for personalized help.',
    },
  ];

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
      >
        <source src="/bg-video.mp4" type="video/mp4" />
      </video>

      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/65 z-10" />

      {/* Content */}
      <div className="relative z-20 flex flex-col min-h-screen">

        {/* Hero Section — two-column split */}
        <section className="flex flex-col lg:flex-row items-center justify-center flex-1 px-6 py-16 gap-8 lg:gap-16 max-w-6xl mx-auto w-full">

          {/* LEFT — Logo + info + CTA */}
          <div className="flex flex-col items-center lg:items-start text-center lg:text-left flex-1">
            <img
              src="/40THAnniv_Logo.png"
              alt="SACLI Logo"
              className="w-28 h-28 object-contain drop-shadow-xl mb-6"
            />
            <h1 className="text-6xl font-extrabold text-white tracking-tight mb-3 drop-shadow-lg">
              ADMIT
            </h1>
            <p className="text-yellow-300 text-sm tracking-widest uppercase mb-5">
              SACLI Admissions Assistant
            </p>
            <p className="text-white/75 text-lg max-w-md mb-8 leading-relaxed">
              Your AI-powered guide to SACLI admissions, enrollment, scholarships,
              and everything you need to start your journey.
            </p>
            <TransitionLink
              to="/chat"
              className="inline-block px-10 py-4 rounded-2xl font-bold text-lg text-white bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 shadow-2xl transition-all hover:scale-105 active:scale-95"
            >
              Chat with ADMIT
            </TransitionLink>
          </div>

          {/* RIGHT — Sign in card */}
          <div className="flex-shrink-0 w-full max-w-sm">
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl flex flex-col gap-6">

              {isAuthenticated ? (
                /* Already signed in */
                <div className="flex flex-col items-center gap-4 text-center">
                  <img
                    src={user.avatar_url}
                    alt={user.name}
                    className="w-16 h-16 rounded-full border-2 border-yellow-400 shadow-lg"
                  />
                  <div>
                    <p className="text-white font-semibold text-lg">{user.name}</p>
                    <p className="text-white/50 text-sm truncate">{user.email}</p>
                  </div>
                  <TransitionLink
                    to="/chat"
                    className="w-full text-center px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 shadow-lg transition-all hover:scale-105"
                  >
                    Continue to Chat →
                  </TransitionLink>
                </div>
              ) : (
                /* Sign in prompt */
                <div className="flex flex-col items-center gap-5 text-center">
                  <div>
                    <h2 className="text-white font-bold text-xl mb-1">Welcome back</h2>
                    <p className="text-white/55 text-sm">Sign in to save your chat history and personalize your experience.</p>
                  </div>

                  {/* Google sign-in button */}
                  <button
                    onClick={login}
                    className="w-full flex items-center justify-center gap-3 px-5 py-3 rounded-xl bg-white text-gray-800 font-semibold text-sm hover:bg-gray-100 shadow-lg transition-all hover:scale-105 active:scale-95"
                  >
                    <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Sign in with Google
                  </button>

                  <div className="w-full border-t border-white/10 pt-4">
                    <p className="text-white/40 text-xs uppercase tracking-widest mb-3 text-center">More coming soon</p>
                    <div className="flex flex-col gap-2">
                      {[
                        { icon: '📅', label: 'Application Tracker' },
                        { icon: '📄', label: 'Document Checklist' },
                        { icon: '🔔', label: 'Enrollment Reminders' },
                      ].map((item) => (
                        <div
                          key={item.label}
                          className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 opacity-50 cursor-not-allowed select-none"
                        >
                          <span className="text-lg">{item.icon}</span>
                          <span className="text-white/60 text-sm">{item.label}</span>
                          <span className="ml-auto text-[10px] text-yellow-400/70 uppercase tracking-wider font-medium">Soon</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </section>

        {/* About Section */}
        <section className="px-6 py-12">
          <div className="max-w-3xl mx-auto">
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl text-center">
              <h2 className="text-2xl font-bold text-white mb-4">What is ADMIT?</h2>
              <p className="text-white/80 leading-relaxed">
                ADMIT is an AI-powered admissions assistant built for{' '}
                <span className="text-yellow-300 font-semibold">
                  St. Anne College Lucena, Inc. (SACLI)
                </span>. Ask about admission requirements, enrollment procedures,
                programs offered, tuition fees, scholarships, and more — and get
                instant, accurate answers anytime.
              </p>
            </div>
          </div>
        </section>

        {/* Quick Info Cards */}
        <section className="px-6 py-8">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-xl font-bold text-white/80 text-center mb-6 uppercase tracking-widest">
              What can I help you with?
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {quickInfoCards.map((card) => (
                <TransitionLink
                  key={card.title}
                  to="/chat"
                  className="block backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 text-left hover:bg-white/20 transition-all hover:scale-105 active:scale-95 shadow-lg group"
                >
                  <div className="text-3xl mb-3">{card.icon}</div>
                  <h3 className="text-white font-semibold mb-2 group-hover:text-yellow-300 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-white/60 text-sm leading-relaxed">{card.desc}</p>
                </TransitionLink>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-6 py-8 mt-auto">
          <div className="max-w-5xl mx-auto border-t border-white/20 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img
                src="/40THAnniv_Logo.png"
                alt="SACLI"
                className="w-8 h-8 object-contain"
              />
              <span className="text-white/60 text-sm">
                St. Anne College Lucena, Inc.
              </span>
            </div>
            <p className="text-white/40 text-sm">
              &copy; {new Date().getFullYear()} SACLI — ADMIT Admissions Assistant
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default HomePage;
