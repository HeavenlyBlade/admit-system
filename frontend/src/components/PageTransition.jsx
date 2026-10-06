/**
 * PageTransition - Wraps page content with a smooth enter animation.
 * Mount it with a unique key per route in App.jsx so React remounts it
 * on every navigation, triggering the enter animation fresh every time.
 */
const PageTransition = ({ children }) => (
  <div
    id="page-transition-wrapper"
    style={{animation: 'pageEnter 0.4s ease-out forwards'}}
  >
    {children}
  </div>
);

export default PageTransition;
