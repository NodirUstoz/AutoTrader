import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import useAuth from '../../hooks/useAuth';

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isAuthenticated, user, logout, isDealer } = useAuth();
  const comparisonIds = useSelector((state) => state.vehicles.comparisonIds);
  const navigate = useNavigate();

  const toggleMenu = () => setMenuOpen((prev) => !prev);

  return (
    <header className="header">
      <div className="header__container">
        <Link to="/" className="header__logo">
          <span className="header__logo-icon">AT</span>
          <span className="header__logo-text">AutoTrader</span>
        </Link>

        <nav className={`header__nav ${menuOpen ? 'header__nav--open' : ''}`}>
          <Link to="/search" className="header__link" onClick={() => setMenuOpen(false)}>
            Search
          </Link>
          <Link to="/financing" className="header__link" onClick={() => setMenuOpen(false)}>
            Financing
          </Link>
          {comparisonIds.length > 0 && (
            <Link to="/compare" className="header__link header__link--compare" onClick={() => setMenuOpen(false)}>
              Compare ({comparisonIds.length})
            </Link>
          )}
          {isAuthenticated && isDealer && (
            <Link to="/listings/create" className="header__link header__link--sell" onClick={() => setMenuOpen(false)}>
              Sell a Vehicle
            </Link>
          )}
        </nav>

        <div className="header__actions">
          {isAuthenticated ? (
            <div className="header__user-menu">
              <button
                className="header__user-button"
                onClick={() => navigate('/dashboard')}
                title="Dashboard"
              >
                {user?.first_name?.[0]?.toUpperCase() || 'U'}
              </button>
              <button className="header__logout-button" onClick={logout}>
                Log out
              </button>
            </div>
          ) : (
            <div className="header__auth-buttons">
              <Link to="/login" className="header__btn header__btn--outline">
                Log in
              </Link>
              <Link to="/register" className="header__btn header__btn--primary">
                Sign up
              </Link>
            </div>
          )}
          <button className="header__menu-toggle" onClick={toggleMenu} aria-label="Toggle menu">
            <span className="header__menu-bar" />
            <span className="header__menu-bar" />
            <span className="header__menu-bar" />
          </button>
        </div>
      </div>
    </header>
  );
}
