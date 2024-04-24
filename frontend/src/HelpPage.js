import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function HelpPage() {
  const navigate = useNavigate();
  useEffect(() => {
    if(!localStorage.getItem('id')){
      navigate('/login')
    }
  }, [])
  return (
    <div>
      <h1>Help Page</h1>
      <p>Here you can find some help!</p>
    </div>
  );
}

export default HelpPage;
