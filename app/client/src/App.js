import './App.css';
import React, { useState, useCallback, useRef, useEffect } from 'react';
import Webcam from "react-webcam";
function App() {
  const webcamRef = useRef(null);
  const FACING_MODE_USER = "user";
  const FACING_MODE_ENVIRONMENT = "environment";
  
  const videoConstraints = {
    facingMode: FACING_MODE_USER
  };
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [screenshot, setScreenshot] = useState(null);
  const [intervalId, setIntervalId] = useState(null);
  const [ lengthROIs, setLengthROIs] = useState(null);
  const [ stop, setStop] = useState(false);
  const [facingMode, setFacingMode] = React.useState(FACING_MODE_USER);
  const startInterval = () => {
    const id = setInterval(capture, 2000); // Adjust the interval time as needed (5000 milliseconds = 5 seconds)
    setIntervalId(id);
  };

  const stopInterval = () => {
    clearInterval(intervalId);
    setIntervalId(null);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const showNewSpeed = (speed) => {
    if (speed!=0) {
      setLengthROIs(speed);
    }
  }


  const handleUpload = () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('photo', selectedFile);

      fetch('/upload', {
        method: 'POST',
        body: formData,
      })
        .then(response => response.json())
        .then(data => {
          console.log('Upload successful', data);
          setResult(data.result);
          showNewSpeed(data.result)

          // Handle success, if needed
        })
        .catch(error => {
          console.error('Error during upload', error);
          // Handle error, if needed
        });
    }
  };

  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setScreenshot(imageSrc);
    const blob = await fetch(imageSrc).then((res) => res.blob());

    const formData = new FormData();
    formData.append('photo', blob);

    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        console.log('Upload successful', data);
        setResult(data.result);
        showNewSpeed(data.result)

        // Handle success, if needed
      })
      .catch(error => {
        console.error('Error during upload', error);
        // Handle error, if needed
      });
  }, [webcamRef]);

  const handleSwitch = React.useCallback(() => {
    setFacingMode(
      prevState =>
        prevState === FACING_MODE_USER
          ? FACING_MODE_ENVIRONMENT
          : FACING_MODE_USER
    );
  }, []);


// useEffect(() => {
//   startInterval();

//   // Cleanup interval when component unmounts
//   return () => {
//     stopInterval();
//   };
// }, []);

  return (
    <div className="App">
      <section class="bg-white dark:bg-gray-900 h-screen ">
        <div class="py-8 px-4 mx-auto max-w-screen-xl text-center lg:py-16 lg:px-12">

          <h1 class="mb-4 text-4xl font-extrabold tracking-tight leading-none text-gray-900 md:text-5xl lg:text-6xl dark:text-white">Hady 34an T3dy</h1>
          <p class="mb-8 text-lg font-normal text-gray-500 lg:text-xl sm:px-16 xl:px-48 dark:text-gray-400">
            Upload a photo and we will tell what speed you should drive at.
          </p>
          <div className='px-48 my-8'>

            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="file_input">Upload file</label>
            <input onChange={handleFileChange} class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="file_input" type="file" />

          </div>
          <div class="flex mb-8 lg:mb-16   sm:justify-center">
            <button onClick={handleUpload} type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
              Upload Photo</button>
          </div>
          <div className="container justify-center flex">
            <Webcam height={1080} width={720} audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
          ...videoConstraints,
          facingMode
        }} />
          </div>
          <h1 className='text-white text-6xl font-bold'>Current Speed Is</h1>
          <h1 className='text-white text-8xl font-extrabold'>{lengthROIs}</h1>
          <button onClick={capture} type="button" class="text-white my-20 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2  dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
            Capture Photo</button>
            <button onClick={stopInterval} type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
              Stop</button>
              <button onClick={handleSwitch}>Switch camera</button>

            <div className=" justify-center flex">

          {/* {screenshot && <img src={screenshot} alt="Captured Screenshot" />} */}
</div>


        </div>
      </section>
    </div>
  );
}

export default App;
