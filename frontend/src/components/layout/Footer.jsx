import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__container">
        <div className="footer__grid">
          <div className="footer__section">
            <h3 className="footer__heading">AutoTrader</h3>
            <p className="footer__text">
              The trusted marketplace for buying and selling vehicles.
              Find cars, trucks, motorcycles, and more from dealers and
              private sellers across the country.
            </p>
          </div>

          <div className="footer__section">
            <h4 className="footer__subheading">Browse</h4>
            <ul className="footer__links">
              <li><Link to="/search?condition=new">New Cars</Link></li>
              <li><Link to="/search?condition=used">Used Cars</Link></li>
              <li><Link to="/search?condition=certified">Certified Pre-Owned</Link></li>
              <li><Link to="/search?vehicle_type=truck">Trucks</Link></li>
              <li><Link to="/search?vehicle_type=suv">SUVs</Link></li>
              <li><Link to="/search?vehicle_type=motorcycle">Motorcycles</Link></li>
            </ul>
          </div>

          <div className="footer__section">
            <h4 className="footer__subheading">Tools</h4>
            <ul className="footer__links">
              <li><Link to="/financing">Financing Calculator</Link></li>
              <li><Link to="/compare">Compare Vehicles</Link></li>
              <li><Link to="/search">Advanced Search</Link></li>
            </ul>
          </div>

          <div className="footer__section">
            <h4 className="footer__subheading">Sell</h4>
            <ul className="footer__links">
              <li><Link to="/listings/create">List Your Vehicle</Link></li>
              <li><Link to="/register">Create Dealer Account</Link></li>
              <li><Link to="/dashboard">Manage Listings</Link></li>
            </ul>
          </div>
        </div>

        <div className="footer__bottom">
          <p className="footer__copyright">
            &copy; {currentYear} AutoTrader. All rights reserved.
          </p>
          <div className="footer__legal">
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
            <a href="/contact">Contact Us</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
