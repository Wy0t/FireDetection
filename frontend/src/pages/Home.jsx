import React, { useState } from 'react';
import Box from '@mui/material/Box';
import '../css/Home.css';
function Home() {
    const [dragging, setDragging] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragging(true);
    };

    const handleDragLeave = () => {
        setDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        const files = Array.from(e.dataTransfer.files);
        // 处理文件上传
        console.log(files);
    };

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        // 处理文件上传
        console.log(files);
    };


    return (
      <>
        <div className='main'>
            <div>
                <Box
                    sx={{
                    width: 550,
                    height: 450,
                    borderRadius: 1,
                    bgcolor: 'primary.main',
                    opacity: 0.5,             // 设置透明度
                    }}
                >
                <h1 style={{ margin: 0 }}>UpLoad Video here</h1>
                <input
                    type="file"
                    accept="video/*"
                    multiple
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                    id="fileInput"
                    />
                    <label htmlFor="fileInput" style={{ cursor: 'pointer' }}>
                    Click or Drag and Drop
                    </label>
                </Box>
            </div>
            <div>
                <Box
                    sx={{
                    width: 550,
                    height: 450,
                    borderRadius: 1,
                    bgcolor: 'primary.main',
                    opacity: 0.5,             // 设置透明度
                    }}
                >    
                </Box>
            </div>
        </div>
      </>
    )
  }
  
  export default Home
  