/**
 * HomePage - Primary landing page for ADMIT
 */
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

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

        {/* Hero Section */}
        <section className="flex flex-col items-center justify-center flex-1 px-6 py-20 text-center">
          <img
            src="/40THAnniv_Logo.png"
            alt="SACLI Logo"
            className="w-28 h-28 object-contain drop-shadow-xl mb-6"
          />
          <h1 className="text-5xl font-extrabold text-white tracking-tight mb-3 drop-shadow-lg">
            ADMIT
          </h1>
          <p className="text-yellow-300 text-sm tracking-widest uppercase mb-4">
            SACLI Admissions Assistant
          </p>
          <p className="text-white/75 text-lg max-w-xl mb-10">
            Your AI-powered guide to SACLI admissions, enrollment, scholarships,
            and everything you need to start your journey.
          </p>
          <button
            onClick={() => navigate('/chat')}
            className="px-10 py-4 rounded-2xl font-bold text-lg text-white bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 shadow-2xl transition-all hover:scale-105 active:scale-95"
          >
            Chat with ADMIT
          </button>
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
                <button
                  key={card.title}
                  onClick={() => navigate('/chat')}
                  className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-6 text-left hover:bg-white/20 transition-all hover:scale-105 active:scale-95 shadow-lg group"
                >
                  <div className="text-3xl mb-3">{card.icon}</div>
                  <h3 className="text-white font-semibold mb-2 group-hover:text-yellow-300 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-white/60 text-sm leading-relaxed">{card.desc}</p>
                </button>
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
