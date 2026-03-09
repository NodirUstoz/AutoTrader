import React from 'react';
import { Route, Routes } from 'react-router-dom';

import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import SearchResultsPage from './pages/SearchResultsPage';
import VehicleDetailPage from './pages/VehicleDetailPage';
import DealerPage from './pages/DealerPage';
import ComparisonPage from './pages/ComparisonPage';
import FinancingPage from './pages/FinancingPage';
import DashboardPage from './pages/DashboardPage';
import ListingCreatePage from './pages/ListingCreatePage';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';

function App() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchResultsPage />} />
          <Route path="/vehicles/:id" element={<VehicleDetailPage />} />
          <Route path="/dealers/:id" element={<DealerPage />} />
          <Route path="/compare" element={<ComparisonPage />} />
          <Route path="/compare/:id" element={<ComparisonPage />} />
          <Route path="/financing" element={<FinancingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/listings/create" element={<ListingCreatePage />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
