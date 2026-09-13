/**
 * LabLine Role-Based Route & Console Guard
 * Enforces authenticated sessions and role permissions before protected consoles render.
 * Protects: /admin/* (admin only) and /technician/* (technician and admin)
 */
(function() {
  const currentPath = window.location.pathname.toLowerCase().replace(/\\/g, '/');
  const rawUser = localStorage.getItem('labline_user');

  function redirectToLogin(reason) {
    if (reason) {
      sessionStorage.setItem('labline_auth_error', reason);
    }
    const redirectTarget = currentPath.includes('/admin/') || currentPath.includes('/technician/') || currentPath.includes('/patient/')
      ? '../index.html'
      : 'index.html';
    window.location.replace(redirectTarget);
  }

  if (!rawUser) {
    redirectToLogin('Authentication required. Please sign in.');
    return;
  }

  try {
    const user = JSON.parse(rawUser);
    const role = (user && user.role) ? user.role.toLowerCase() : '';

    if (currentPath.includes('/admin/')) {
      if (role !== 'admin') {
        redirectToLogin('Access Denied: Administrator role required to access admin console.');
        return;
      }
    } else if (currentPath.includes('/technician/')) {
      if (role !== 'technician' && role !== 'admin') {
        redirectToLogin('Access Denied: Clinical Technician role required to access laboratory console.');
        return;
      }
    }
  } catch (err) {
    redirectToLogin('Invalid session data. Please sign in again.');
  }
})();
