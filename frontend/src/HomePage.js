import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import './App.css';
import Navbar from './Navbar';

function HomePage() {
    let navigate = useNavigate();

    function handleClick() {
      navigate('/transferPage');
    }

  useEffect(() => {
    if(!localStorage.getItem('id')){
      navigate('/login')
    }
  }, [])
  
  return (
  
      <div className="HomePage">
      <h1>
      <span className="color-1">L</span>
      <span className="color-2">O</span>
      <span className="color-3">V</span>
      <span className="color-1">E</span>
      <span className="color-2">L</span>
      <span className="color-3">Y</span>
      <span className="color-1">T</span>
      <span className="color-2">R</span>
      <span className="color-3">A</span>
      <span className="color-1">N</span>
      <span className="color-2">S</span>
      <span className="color-3">F</span>
      <span className="color-1">E</span>
      <span className="color-2">R</span>
     
      </h1> 
      <Navbar/>
      
    <div className='image-section1'>
        <img src='/originPicture.jpg'/>
      </div>

      <div className='image-section2'>
        <img src='/afterTransfer.png'/>
      </div>

      <div className='main-word'>
        <h2>Creating joy</h2>
        <h3>Start uploading your images and changing styles</h3>
        <button onClick={handleClick}>Start</button>
        </div>
      </div>
     
    
  );
}


  
  

 

export default HomePage;
