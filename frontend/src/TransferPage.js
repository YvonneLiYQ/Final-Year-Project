import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';

function ImageTransferPage() {
  const navigate = useNavigate();
  const [contentImage, setContentImage] = useState(null);
  const [styleImage, setStyleImage] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [contentFile, setContentFile] = useState(null);  // 保存文件本身以便上传
  const [styleFile, setStyleFile] = useState(null);

  const uploadFile = (event, setImage, setFile) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setImage(imageUrl);
      setFile(file);  // 保存文件
    }
  };

  const performImageTransfer = () => {
    if (!contentFile || !styleFile) {
      alert("Please upload both content and style images first.");
      return;
    }

    const formData = new FormData();
    formData.append('content', contentFile);
    formData.append('style', styleFile);

    fetch('http://127.0.0.1:5000/submit', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      setResultImage(data.result);  // 假设返回的JSON对象中有result_url字段
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to transfer image style.');
    });
  };

  useEffect(() => {
    if (!localStorage.getItem('id')) {
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div>
      <Navbar />
      <h1>Image Transfer Sample</h1>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '120px', marginTop: '16px' }}>
        <div>
          <input type="file" accept="image/*" onChange={(e) => uploadFile(e, setContentImage, setContentFile)} style={{ display: 'none' }} id="contentUpload" />
          <button onClick={() => document.getElementById('contentUpload').click()}>Upload Content Image</button>
          {contentImage && <img src={contentImage} alt="Content Image" style={{ width: '200px', display: 'block', marginTop: '10px' }} />}
        </div>
        <div>
          <input type="file" accept="image/*" onChange={(e) => uploadFile(e, setStyleImage, setStyleFile)} style={{ display: 'none' }} id="styleUpload" />
          <button onClick={() => document.getElementById('styleUpload').click()}>Upload Style Image</button>
          {styleImage && <img src={styleImage} alt="Style Image" style={{ width: '200px', display: 'block', marginTop: '10px' }} />}
        </div>
      </div>
      {resultImage && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <img src={resultImage} alt="Result Image" style={{ width: '200px' }} />
        </div>
      )}
      <button onClick={performImageTransfer} style={{ margin: '20px auto', display: 'block' }}>Execute Image Transfer</button>
    </div>
  );
}

export default ImageTransferPage;
