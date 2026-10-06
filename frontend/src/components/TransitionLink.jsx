/**
 * TransitionLink - Intercepts navigation clicks, plays an exit animation
 * on the current page wrapper, then navigates after 300ms.
 */
import { useNavigate } from 'react-router-dom';

export default function TransitionLink({ to, children, className }) {
  const navigate = useNavigate();

  const handleClick = (e) => {
    e.preventDefault();
    const wrapper = document.getElementById('page-transition-wrapper');
    if (wrapper) {
      wrapper.style.animation = 'pageExit 0.3s ease-in forwards';
      setTimeout(() => navigate(to), 300);
    } else {
      navigate(to);
    }
  };

  return (
    <a href={to} onClick={handleClick} className={className}>
      {children}
    </a>
  );
}
