import React, { useState } from 'react';

const Test = () => {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', 'My Video'); // 可以根据需要添加其他字段

        try {
            const response = await fetch('http://127.0.0.1:8000/app/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    // 如果需要，可以在此处添加其他请求头
                },
            });

            if (response.ok) {
                const data = await response.json();
                alert('Upload successful!');
                console.log(data);
            } else {
                const errorData = await response.json();
                alert('Upload failed.');
                console.error(errorData);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <button type="submit">Upload</button>
            </form>
        </div>
    );
};

export default Test;
