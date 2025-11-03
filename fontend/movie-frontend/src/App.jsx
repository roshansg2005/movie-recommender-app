import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'; // Import our custom theme CSS

const API_URL = 'https://movie-recommender-app-185a.onrender.com';

function App() {
  const [movieList, setMovieList] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState('dark'); 

  // Fetch movie list
  useEffect(() => {
    axios.get(`${API_URL}/movies`)
      .then(response => {
        setMovieList(response.data);
        if (response.data.length > 0) {
          setSelectedMovie(response.data[0]);
        }
      })
      .catch(error => {
        console.error('Error fetching movie list:', error);
      });
  }, []);

  // Manage Theme Class on Body
  useEffect(() => {
    document.body.className = theme === 'light' ? 'light-theme' : '';
  }, [theme]); 

  // Toggle Theme Function
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  // Recommendation Function
  const handleRecommend = () => {
    setLoading(true);
    setRecommendations([]); 
    
    axios.get(`${API_URL}/recommend`, {
      params: { movie: selectedMovie }
    })
      .then(response => {
        setRecommendations(response.data);
      })
      .catch(error => {
        console.error('Error fetching recommendations:', error);
      })
      .finally(() => {
        setLoading(false); 
      });
  };

  // The JSX
  return (
    // Use a React Fragment <> to hold the button and container
    <>
      {/* --- THIS BUTTON IS NOW OUTSIDE THE CONTAINER --- */}
      <button onClick={toggleTheme} className="theme-toggle-btn">
        Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode
      </button>

      <div className="container my-5"> 
        {/* The toggle button was removed from here */}

        {/* --- ADDED 'sticky-top' and 'control-bar-sticky' CLASSES --- */}
        <div className="row justify-content-center g-2 sticky-top control-bar-sticky">
          
          <div className="col-lg-5 col-md-7">
            <select 
              className="form-select form-select-lg" 
              value={selectedMovie} 
              onChange={e => setSelectedMovie(e.target.value)} 
            >
              {movieList.map(movie => (
                <option key={movie} value={movie}>
                  {movie}
                </option>
              ))}
            </select>
          </div>
          
          <div className="col-lg-3 col-md-5 d-grid">
            <button 
              className="btn btn-spotify btn-lg"
              onClick={handleRecommend} 
              disabled={loading}
            >
              {loading ? 'Finding...' : 'Get Recommendations'}
            </button>
          </div>
        </div>
        {/* --- END OF MOVED SECTION --- */}

        <header className="text-center mt-4 mb-5 App-header">
          <h1 className="fw-bold display-">Movie Recommender</h1>
          <p className="text-muted fs-5">Discover your next favorite film!</p>
        </header>

        <main>
          {loading && <p className="text-center text-muted">Finding your perfect movies...</p>}
          
          <div className="row row-cols-2 row-cols-md-3 row-cols-lg-5 g-4">
            {recommendations.map(movie => (
              <div key={movie.title} className="col">
                <div className="card h-100">
                  <img src={movie.poster} className="card-img-top" alt={movie.title} />
                  <div className="card-body text-center">
                    <h6 className="card-title">{movie.title}</h6>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
        
        <footer className="text-center mt-5 pt-3">
          Built with React, Flask & Bootstrap
        </footer>
      </div>
    </>
  );
}

export default App;