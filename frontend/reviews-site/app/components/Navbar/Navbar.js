import React from 'react';
import Link from 'next/link';
const Navbar = () => {
    return (
    <nav className="navbar">
      <div className="navbar-left">
        <a href="/" className="logo">
          Review Site
        </a>
      </div>
      <div className="navbar-center">
        <ul className="nav-links">
          <li><a href="/movies">Movies</a></li>
          {/*dependent on login*/}
          <li><a href="/user">Your Profile</a></li>
        </ul>
      </div>
      <div className="navbar-right">
        <a href="/cart" className="cart-icon">
          <i className="fas fa-shopping-cart"></i>
          <span className="cart-count">0</span>
        </a>
        <a href="/account" className="user-icon">
          <i className="fas fa-user"></i>
        </a>
      </div>
    </nav>
    );
};

export default Navbar;