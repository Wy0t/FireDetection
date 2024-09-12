import React, { useCallback, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { useDropzone } from 'react-dropzone';
import '../css/Home.css';

function Home() {
  const [videoFile, setVideoFile] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const onDrop = useCallback(acceptedFiles => {
    setVideoFile(acceptedFiles[0]); // 保存选中的影片文件
    setUploadSuccess(true); // 设置上传成功状态
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: 'video/*', // 只接受影片文件
  });

  const handleCancel = () => {
    setVideoFile(null); // 重置选中的文件
    setUploadSuccess(false); // 取消上传成功状态
  };

  const boxStyles = {
    width: 550,
    height: 450,
    borderRadius: 1,
    bgcolor: 'primary.main',
    opacity: 0.5, // 设置透明度
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  };

  return (
    <>
      <div className="main">
        <div>
          <Box sx={boxStyles}>
            {/* 虛線框範圍 */}
            <div
              {...getRootProps()}
              style={{
                border: '2px dashed #ccc',
                borderRadius: '8px',
                width: '100%',
                height: '60%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer', // 只在虛線框區域設置游標為手指型
              }}
            >
              <input {...getInputProps()} />
              {!uploadSuccess && <p>Drag & Drop your video file here</p>}
              {videoFile && <p>{videoFile.name}</p>} {/* 顯示影片文件名稱 */}
            </div>

            {/* 按鈕區域 */}
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              {videoFile && (
                <>
                  <Button variant="contained" color="primary">
                    Upload
                  </Button>
                  <Button variant="contained" color="error" onClick={handleCancel}>
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </Box>
        </div>

        <div>
          <Box sx={boxStyles}>
            {/* 第二个 Box 保持空白，作为后端返回文件展示的占位符 */}
          </Box>
        </div>
      </div>
    </>
  );
}

export default Home;
