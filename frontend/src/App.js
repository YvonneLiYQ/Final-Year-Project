import React from 'react';
import { Route, Routes } from 'react-router-dom';
import ReviewPage from './pages/ReviewPage';
import TransferPage from './TransferPage';
import HelpPage from './HelpPage';
import HomePage from './HomePage';
import Login from './pages/Login';
import Register from './pages/Register';

import './App.css';


function App() {
  return (
    <div className="App">
      <Routes>
          <Route path="/login" element={<Login/>}/>
          <Route path="/register" element={<Register/>}/>
          <Route path="/" element={<HomePage/>}/>
          <Route path="/reviewPage" element={<ReviewPage/>} />
          <Route path="/helpPage" element={<HelpPage/>} />
          <Route path="/transferPage" element={<TransferPage/>} />
      </Routes>
     </div>
  );
}


  

 

export default App;
