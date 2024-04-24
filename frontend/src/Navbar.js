import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/">homepage</Link>
      <Link to="/transferPage">transferPage</Link>
      <Link to="/reviewPage">reviewpage</Link>
      <Link to="/helpPage">help</Link>
      
    </nav>
  );
}

export default Navbar;
