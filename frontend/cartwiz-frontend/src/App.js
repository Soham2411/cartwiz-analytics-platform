// src/App.js - Enhanced with Interactive Filtering
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import './darkmode.css';

const API_BASE_URL = 'http://localhost:8000/api/analytics';

function App() {
  const [overviewData, setOverviewData] = useState(null);
  const [regionalData, setRegionalData] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loyaltyData, setLoyaltyData] = useState([]);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [darkMode, setDarkMode] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [entityDetails, setEntityDetails] = useState(null);
  const [showSearchModal, setShowSearchModal] = useState(false);

  // Add ML predictions state (for next feature)
  const [mlPredictions, setMlPredictions] = useState(null);
  const [showMLSection, setShowMLSection] = useState(false);
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filter states
  const [selectedYear, setSelectedYear] = useState('2024');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeFilters, setActiveFilters] = useState(false);

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
  }, []);

// Apply dark theme class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }, [darkMode]);

  useEffect(() => {
    fetchAllData();
  }, [selectedYear, selectedRegion, selectedCategory]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Build query parameters based on filters
      const params = new URLSearchParams();
      if (selectedYear !== 'all') params.append('year', selectedYear);
      if (selectedRegion !== 'all') params.append('region', selectedRegion);
      if (selectedCategory !== 'all') params.append('category', selectedCategory);

      const [overview, regional, products, loyalty, trends, categories] = await Promise.all([
        axios.get(`${API_BASE_URL}/overview/?${params}`),
        axios.get(`${API_BASE_URL}/regional-sales/?${params}`),
        axios.get(`${API_BASE_URL}/top-products/?limit=10&${params}`),
        axios.get(`${API_BASE_URL}/customer-loyalty/?${params}`),
        axios.get(`${API_BASE_URL}/monthly-trends/?year=${selectedYear}&${params}`),
        axios.get(`${API_BASE_URL}/category-performance/?${params}`)
      ]);

      setOverviewData(overview.data);
      setRegionalData(regional.data);
      setTopProducts(products.data);
      setLoyaltyData(loyalty.data);
      
      // Format monthly trends
      setMonthlyTrends(trends.data.map(item => ({
        ...item,
        month: new Date(item.month).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
        monthly_revenue: parseFloat(item.monthly_revenue) / 1000000 // Convert to millions
      })));

      setCategoryData(categories.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const toggleDarkMode = () => {
  setDarkMode(!darkMode);
  localStorage.setItem('darkMode', !darkMode);
  };

  const fetchMLData = async () => {
  try {
    const mlResponse = await axios.get(`${API_BASE_URL}/ml-predictions/`);
    setMlPredictions(mlResponse.data);
    } catch (error) {
    console.error('Error fetching ML predictions:', error);
    }
  };

  const resetFilters = () => {
    setSelectedYear('2024');
    setSelectedRegion('all');
    setSelectedCategory('all');
    setActiveFilters(false);
  };

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading Enterprise Data...</span>
        </div>
        <div className="ms-3">
          <h5>Loading Your $4B Dataset...</h5>
          <p className="text-muted">Processing 10M+ transactions</p>
        </div>
      </div>
    );
  }

  const performSearch = async (query) => {
  if (!query || query.length < 2) return;
  
  setSearchLoading(true);
  try {
    const response = await axios.get(`${API_BASE_URL}/search/?q=${encodeURIComponent(query)}`);
    setSearchResults(response.data);
  } catch (error) {
    console.error('Search error:', error);
  }
  setSearchLoading(false);
};

const getEntityDetails = async (entityType, entityId) => {
  setSearchLoading(true);
  try {
    const response = await axios.get(`${API_BASE_URL}/${entityType}/${entityId}/`);
    setEntityDetails(response.data);
    setShowSearchModal(true);
  } catch (error) {
    console.error('Entity details error:', error);
  }
  setSearchLoading(false);
};

  return (
    <div className="App">
      {/* Enhanced Header */}
      {/* Enhanced Header with Dark Mode Toggle */}
      <nav className="navbar navbar-dark bg-dark mb-4">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1 d-flex align-items-center">
            <span className="me-2">🛍️</span>
            CartWiz Analytics Platform
            <span className="badge bg-success ms-2">Enterprise</span>
          </span>
          <div className="d-flex align-items-center gap-3">
            <span className="navbar-text">
              Enterprise Retail Intelligence | 10M+ Transactions
            </span>
            <button 
              className={`theme-toggle ${darkMode ? 'dark' : ''}`}
              onClick={toggleDarkMode}
              title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
            />
            <span className={`badge ${activeFilters ? 'bg-warning' : 'bg-success'}`}>
              {activeFilters ? 'Filtered View' : 'Full Dataset'}
            </span>
          </div>
        </div>
      </nav>

      <div className="container-fluid">
        
        {/* Interactive Filters */}
        <div className="card mb-4">
          <div className="card-header">
            <div className="row align-items-center">
              <div className="col">
                <h5 className="mb-0">🔍 Interactive Filters</h5>
              </div>
              <div className="col-auto">
                <button 
                  className="btn btn-outline-secondary btn-sm"
                  onClick={resetFilters}
                >
                  Reset All Filters
                </button>
              </div>
            </div>
          </div>
          <div className="card-body">
            <div className="row g-3">
              <div className="col-md-3">
                <label className="form-label">Year</label>
                <select 
                  className="form-select"
                  value={selectedYear}
                  onChange={(e) => {
                    setSelectedYear(e.target.value);
                    setActiveFilters(e.target.value !== '2024' || selectedRegion !== 'all' || selectedCategory !== 'all');
                  }}
                >
                  <option value="2024">2024</option>
                  <option value="2023">2023</option>
                  <option value="all">All Years</option>
                </select>
              </div>
              <div className="col-md-3">
                <label className="form-label">Region</label>
                <select 
                  className="form-select"
                  value={selectedRegion}
                  onChange={(e) => {
                    setSelectedRegion(e.target.value);
                    setActiveFilters(selectedYear !== '2024' || e.target.value !== 'all' || selectedCategory !== 'all');
                  }}
                >
                  <option value="all">All Regions</option>
                  <option value="Southeast">Southeast</option>
                  <option value="Midwest">Midwest</option>
                  <option value="Northeast">Northeast</option>
                  <option value="West">West</option>
                  <option value="Southwest">Southwest</option>
                </select>
              </div>
              <div className="col-md-3">
                <label className="form-label">Category</label>
                <select 
                  className="form-select"
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setActiveFilters(selectedYear !== '2024' || selectedRegion !== 'all' || e.target.value !== 'all');
                  }}
                >
                  <option value="all">All Categories</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Apparel">Apparel</option>
                  <option value="Home & Garden">Home & Garden</option>
                  <option value="Groceries">Groceries</option>
                  <option value="Sports & Outdoors">Sports & Outdoors</option>
                </select>
              </div>
              <div className="col-md-3 d-flex align-items-end">
                <div className="w-100">
                  <div className="text-muted small">
                    {activeFilters ? '📊 Filtered Results' : '🌐 Complete Dataset'}
                  </div>
                  <div className="fw-bold">
                    {overviewData ? formatNumber(overviewData.total_transactions) : '0'} transactions
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Advanced Search Section */}
<div className="card mb-4">
  <div className="card-header">
    <h5 className="mb-0">🔍 Advanced Search & Analytics</h5>
  </div>
  <div className="card-body">
    <div className="row align-items-center">
      <div className="col-md-6">
        <div className="input-group">
          <span className="input-group-text">🔍</span>
          <input
            type="text"
            className="form-control"
            placeholder="Search products, stores, customers..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              if (e.target.value.length >= 2) {
                performSearch(e.target.value);
              } else {
                setSearchResults(null);
              }
            }}
          />
          {searchLoading && (
            <span className="input-group-text">
              <div className="spinner-border spinner-border-sm" role="status"></div>
            </span>
          )}
        </div>
      </div>
      <div className="col-md-6 text-md-end mt-2 mt-md-0">
        <div className="btn-group" role="group">
          <button 
            className="btn btn-outline-primary btn-sm"
            onClick={() => window.open(`${API_BASE_URL}/trending/?days=30`, '_blank')}
          >
            📈 Trending Products
          </button>
          <button 
            className="btn btn-outline-success btn-sm"
            onClick={() => window.open(`${API_BASE_URL}/competitive/?category=Electronics`, '_blank')}
          >
            🏆 Competitive Analysis
          </button>
        </div>
      </div>
    </div>

    {/* Search Results */}
    {searchResults && searchResults.total_results > 0 && (
      <div className="mt-3">
        <div className="row">
          {/* Products Results */}
          {searchResults.products.length > 0 && (
            <div className="col-md-4">
              <h6 className="text-primary">🛍️ Products ({searchResults.products.length})</h6>
              <div className="list-group">
                {searchResults.products.map((product, index) => (
                  <button
                    key={index}
                    className="list-group-item list-group-item-action d-flex justify-content-between align-items-start"
                    onClick={() => getEntityDetails('product', product.id)}
                  >
                    <div>
                      <div className="fw-bold">{product.name.substring(0, 30)}...</div>
                      <small className="text-muted">{product.category} | {product.brand}</small>
                    </div>
                    <span className="badge bg-primary rounded-pill">${product.price}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Stores Results */}
          {searchResults.stores.length > 0 && (
            <div className="col-md-4">
              <h6 className="text-success">🏪 Stores ({searchResults.stores.length})</h6>
              <div className="list-group">
                {searchResults.stores.map((store, index) => (
                  <button
                    key={index}
                    className="list-group-item list-group-item-action"
                    onClick={() => getEntityDetails('store', store.id)}
                  >
                    <div className="fw-bold">{store.name}</div>
                    <small className="text-muted">{store.city}, {store.state} | {store.type}</small>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Customers Results */}
          {searchResults.customers.length > 0 && (
            <div className="col-md-4">
              <h6 className="text-info">👥 Customers ({searchResults.customers.length})</h6>
              <div className="list-group">
                {searchResults.customers.map((customer, index) => (
                  <button
                    key={index}
                    className="list-group-item list-group-item-action"
                    onClick={() => getEntityDetails('customer', customer.id)}
                  >
                    <div className="fw-bold">Customer {customer.id.slice(-4)}</div>
                    <small className="text-muted">{customer.tier} | {customer.channel}</small>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )}

    {searchResults && searchResults.total_results === 0 && searchQuery.length >= 2 && (
      <div className="mt-3 text-center text-muted">
        <div className="py-4">
          <div className="display-6">🔍</div>
          <p>No results found for "{searchQuery}"</p>
          <small>Try searching for product names, store cities, or customer tiers</small>
        </div>
      </div>
    )}
  </div>
</div>

{/* Entity Details Modal */}
{showSearchModal && entityDetails && (
  <div className="modal show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
    <div className="modal-dialog modal-lg">
      <div className={`modal-content ${darkMode ? 'bg-dark text-light' : ''}`}>
        <div className="modal-header">
          <h5 className="modal-title">
            {entityDetails.product && `🛍️ ${entityDetails.product.name}`}
            {entityDetails.store && `🏪 ${entityDetails.store.name}`}
            {entityDetails.customer && `👥 Customer ${entityDetails.customer.id.slice(-4)}`}
          </h5>
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => setShowSearchModal(false)}
          ></button>
        </div>
        <div className="modal-body">
          
          {/* Product Details */}
          {entityDetails.product && (
            <div>
              <div className="row mb-3">
                <div className="col-md-6">
                  <strong>Category:</strong> {entityDetails.product.category}<br/>
                  <strong>Brand:</strong> {entityDetails.product.brand}<br/>
                  <strong>Price:</strong> ${entityDetails.product.msrp}<br/>
                  <strong>Margin:</strong> {entityDetails.product.margin.toFixed(1)}%
                </div>
                <div className="col-md-6">
                  <strong>Total Revenue:</strong> ${entityDetails.performance.total_revenue?.toLocaleString() || 0}<br/>
                  <strong>Units Sold:</strong> {entityDetails.performance.units_sold?.toLocaleString() || 0}<br/>
                  <strong>Transactions:</strong> {entityDetails.performance.total_transactions?.toLocaleString() || 0}<br/>
                  <strong>Avg Price:</strong> ${entityDetails.performance.avg_price?.toFixed(2) || 0}
                </div>
              </div>
              
              {entityDetails.top_stores && entityDetails.top_stores.length > 0 && (
                <div className="mt-3">
                  <h6>🏆 Top Performing Stores</h6>
                  <div className="table-responsive">
                    <table className="table table-sm">
                      <thead>
                        <tr>
                          <th>Store</th>
                          <th>Location</th>
                          <th>Revenue</th>
                          <th>Units</th>
                        </tr>
                      </thead>
                      <tbody>
                        {entityDetails.top_stores.slice(0, 5).map((store, index) => (
                          <tr key={index}>
                            <td>{store.store__store_name}</td>
                            <td>{store.store__city}, {store.store__state}</td>
                            <td>${store.revenue.toLocaleString()}</td>
                            <td>{store.units}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Store Details */}
          {entityDetails.store && (
            <div>
              <div className="row mb-3">
                <div className="col-md-6">
                  <strong>Address:</strong> {entityDetails.store.address}<br/>
                  <strong>City:</strong> {entityDetails.store.city}, {entityDetails.store.state}<br/>
                  <strong>Type:</strong> {entityDetails.store.type}<br/>
                  <strong>Manager:</strong> {entityDetails.store.manager}
                </div>
                <div className="col-md-6">
                  <strong>Total Revenue:</strong> ${entityDetails.performance.total_revenue?.toLocaleString() || 0}<br/>
                  <strong>Transactions:</strong> {entityDetails.performance.total_transactions?.toLocaleString() || 0}<br/>
                  <strong>Unique Customers:</strong> {entityDetails.performance.unique_customers?.toLocaleString() || 0}<br/>
                  <strong>Avg Transaction:</strong> ${entityDetails.performance.avg_transaction?.toFixed(2) || 0}
                </div>
              </div>

              {entityDetails.top_products && entityDetails.top_products.length > 0 && (
                <div className="mt-3">
                  <h6>🛍️ Top Products</h6>
                  <div className="table-responsive">
                    <table className="table table-sm">
                      <thead>
                        <tr>
                          <th>Product</th>
                          <th>Category</th>
                          <th>Revenue</th>
                          <th>Units</th>
                        </tr>
                      </thead>
                      <tbody>
                        {entityDetails.top_products.slice(0, 5).map((product, index) => (
                          <tr key={index}>
                            <td>{product.product__name.substring(0, 30)}...</td>
                            <td>{product.product__category}</td>
                            <td>${product.revenue.toLocaleString()}</td>
                            <td>{product.units}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Customer Details */}
          {entityDetails.customer && (
            <div>
              <div className="row mb-3">
                <div className="col-md-6">
                  <strong>Loyalty Tier:</strong> <span className="badge bg-info">{entityDetails.customer.tier}</span><br/>
                  <strong>Age Range:</strong> {entityDetails.customer.age_range}<br/>
                  <strong>Channel:</strong> {entityDetails.customer.preferred_channel}<br/>
                  <strong>Member Since:</strong> {new Date(entityDetails.customer.join_date).toLocaleDateString()}
                </div>
                <div className="col-md-6">
                  <strong>Total Spent:</strong> ${entityDetails.behavior.total_spent?.toLocaleString() || 0}<br/>
                  <strong>Transactions:</strong> {entityDetails.behavior.total_transactions?.toLocaleString() || 0}<br/>
                  <strong>Avg Order:</strong> ${entityDetails.behavior.avg_order_value?.toFixed(2) || 0}<br/>
                  <strong>Lifetime Value:</strong> ${entityDetails.customer.lifetime_value?.toLocaleString() || 0}
                </div>
              </div>

              {entityDetails.favorite_categories && entityDetails.favorite_categories.length > 0 && (
                <div className="mt-3">
                  <h6>❤️ Favorite Categories</h6>
                  <div className="row">
                    {entityDetails.favorite_categories.slice(0, 3).map((category, index) => (
                      <div key={index} className="col-md-4 mb-2">
                        <div className="card card-body text-center">
                          <strong>{category.product__category}</strong><br/>
                          <small>${category.spent.toLocaleString()}</small>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
          <div className="modal-footer">
            <button type="button" 
              className="btn btn-secondary" 
              onClick={() => setShowSearchModal(false)}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )}
        {/* Enhanced Overview Cards */}
        {overviewData && (
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center bg-primary text-white h-100">
                <div className="card-body">
                  <div className="display-6">💰</div>
                  <h5 className="card-title">Total Revenue</h5>
                  <h2>{formatCurrency(overviewData.total_revenue)}</h2>
                  <small>
                    {activeFilters ? 'Filtered Results' : 'Across 500 stores nationwide'}
                  </small>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center bg-success text-white h-100">
                <div className="card-body">
                  <div className="display-6">📊</div>
                  <h5 className="card-title">Transactions</h5>
                  <h2>{formatNumber(overviewData.total_transactions)}</h2>
                  <small>
                    {activeFilters ? 'Filtered Dataset' : 'Enterprise-scale dataset'}
                  </small>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center bg-info text-white h-100">
                <div className="card-body">
                  <div className="display-6">👥</div>
                  <h5 className="card-title">Customers</h5>
                  <h2>{formatNumber(overviewData.total_customers)}</h2>
                  <small>Loyalty program members</small>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center bg-warning text-white h-100">
                <div className="card-body">
                  <div className="display-6">💳</div>
                  <h5 className="card-title">Avg Transaction</h5>
                  <h2>{formatCurrency(overviewData.avg_transaction_value)}</h2>
                  <small>Per transaction value</small>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Row 1 - Enhanced */}
        <div className="row mb-4">
          {/* Regional Sales with improved styling */}
          <div className="col-md-8">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">💰 Revenue by Region</h5>
                <div className="badge bg-secondary">
                  {regionalData.length} {regionalData.length === 1 ? 'Region' : 'Regions'}
                </div>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={regionalData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="region" />
                    <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                    <Tooltip 
                      formatter={(value) => formatCurrency(value)}
                      labelStyle={{ color: '#333' }}
                    />
                    <Bar dataKey="total_revenue" fill="#0088FE" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Customer Loyalty with enhanced styling */}
          <div className="col-md-4">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="mb-0">👥 Customer Loyalty Distribution</h5>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={loyaltyData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="customer_count"
                      label={({loyalty_tier, percent}) => `${loyalty_tier} ${(percent * 100).toFixed(0)}%`}
                    >
                      {loyaltyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatNumber(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row 2 - Enhanced */}
        <div className="row mb-4">
          {/* Monthly Trends - Enhanced with Area Chart */}
          <div className="col-md-8">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">📈 {selectedYear} Monthly Revenue Trends</h5>
                <div className="badge bg-info">
                  {monthlyTrends.length} months of data
                </div>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={monthlyTrends} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `$${value}M`} />
                    <Tooltip formatter={(value) => `$${value.toFixed(1)}M`} />
                    <Area 
                      type="monotone" 
                      dataKey="monthly_revenue" 
                      stroke="#00C49F" 
                      fill="#00C49F" 
                      fillOpacity={0.3}
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Top Products - Enhanced */}
          <div className="col-md-4">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">🛍️ Top Products</h5>
                <div className="badge bg-primary">
                  Top {topProducts.length}
                </div>
              </div>
              <div className="card-body" style={{ maxHeight: '350px', overflowY: 'auto' }}>
                <div className="list-group list-group-flush">
                  {topProducts.map((product, index) => (
                    <div key={index} className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                      <div className="flex-grow-1">
                        <div className="d-flex align-items-center mb-1">
                          <span className="badge bg-secondary me-2">#{index + 1}</span>
                          <h6 className="mb-0" style={{ fontSize: '0.9rem' }}>
                            {product.product_name.substring(0, 25)}...
                          </h6>
                        </div>
                        <small className="text-muted">{product.category}</small>
                      </div>
                      <div className="text-end ms-2">
                        <div className="fw-bold text-primary" style={{ fontSize: '0.9rem' }}>
                          {formatCurrency(product.total_revenue)}
                        </div>
                        <small className="text-muted">{formatNumber(product.units_sold)} units</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* New Category Performance Chart */}
        {categoryData.length > 0 && (
          <div className="row mb-4">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">🏷️ Category Performance Analysis</h5>
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={categoryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="product__category" />
                      <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Bar dataKey="total_revenue" fill="#FFBB28" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Data Tables */}
        <div className="row mb-4">
          {/* Regional Details - Enhanced */}
          <div className="col-md-6">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="mb-0">🗺️ Regional Performance Details</h5>
              </div>
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-dark">
                      <tr>
                        <th>Region</th>
                        <th>Revenue</th>
                        <th>Stores</th>
                        <th>Avg/Store</th>
                      </tr>
                    </thead>
                    <tbody>
                      {regionalData.map((region, index) => (
                        <tr key={index}>
                          <td>
                            <strong>{region.region}</strong>
                            {index === 0 && <span className="badge bg-success ms-2">Top</span>}
                          </td>
                          <td className="fw-bold text-primary">{formatCurrency(region.total_revenue)}</td>
                          <td>{region.store_count}</td>
                          <td>{formatCurrency(region.avg_store_revenue)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* Loyalty Details - Enhanced */}
          <div className="col-md-6">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="mb-0">💎 Loyalty Tier Performance</h5>
              </div>
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-dark">
                      <tr>
                        <th>Tier</th>
                        <th>Customers</th>
                        <th>Revenue</th>
                        <th>Revenue/Customer</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loyaltyData.map((tier, index) => (
                        <tr key={index}>
                          <td>
                            <strong>{tier.loyalty_tier}</strong>
                            {tier.loyalty_tier === 'Bronze' && <span className="badge bg-warning ms-2">Volume</span>}
                            {tier.loyalty_tier === 'Platinum' && <span className="badge bg-info ms-2">Premium</span>}
                          </td>
                          <td>{formatNumber(tier.customer_count)}</td>
                          <td className="fw-bold text-success">{formatCurrency(tier.total_revenue)}</td>
                          <td>{formatCurrency(tier.revenue_per_customer)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Footer */}
        <footer className="bg-dark text-white py-4 mt-5">
          <div className="container-fluid">
            <div className="row align-items-center">
              <div className="col-md-6">
                <h5 className="mb-1">CartWiz Analytics Platform</h5>
                <p className="mb-0 text-muted">
                  Enterprise-scale retail intelligence powered by 10M+ transactions
                </p>
              </div>
              <div className="col-md-6 text-md-end">
                <div className="d-flex justify-content-md-end gap-4">
                  <div>
                    <div className="fw-bold">Data Scale</div>
                    <small className="text-muted">$4B+ Revenue</small>
                  </div>
                  <div>
                    <div className="fw-bold">Coverage</div>
                    <small className="text-muted">500 Stores, 50 States</small>
                  </div>
                  <div>
                    <div className="fw-bold">Technology</div>
                    <small className="text-muted">Django + React + PostgreSQL</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </footer>

        {/* Floating Report Button */}
        <button 
          className="fab-report"
          onClick={() => window.open('http://localhost:8000/api/analytics/generate-report/', '_blank')}
          title="Download Executive Report">
          📄
        </button>

      </div>
    </div>
  );
}

export default App;