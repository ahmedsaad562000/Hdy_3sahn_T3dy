import './App.css';
import React, { useState, useCallback, useRef, useEffect } from 'react';
import Webcam from "react-webcam";
import useSound from 'use-sound';
import yalahwy from "./RPReplay_Final1703714630.mp3"
import beraha from "./RPReplay_Final1703714427.mp3"

function App() {
  const webcamRef = useRef(null);
  const FACING_MODE_USER = "user";
  const FACING_MODE_ENVIRONMENT = "environment";

  const videoConstraints = {
    facingMode: FACING_MODE_USER
  };

  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [imagePreview, setImagePreview] = useState(null);
  const [playSound] = useSound(yalahwy);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [screenshots, setScreenshots] = useState([]);
  const [lastChangeAt, setLastChangeAt] = useState(null);
  const [mostRepeatedSpeed, setMostRepeatedSpeed] = useState(null);
  const [changingSpeed, setChangingSpeed] = useState(false);


  const [intervalId, setIntervalId] = useState(100);
  const [speed, setSpeed] = useState(null);
  const [lastSpeedPredictions, setLastSpeedPredictions] = useState([]);
  const [facingMode, setFacingMode] = React.useState(FACING_MODE_USER);

  const [webCamSpeed, setWebCamSpeed] = useState(null);
  const [activeTab, setActiveTab] = useState('Camera');
  const [isCameraOn, setIsCameraOn] = useState(false);

  const handleTabClick = (tabName) => {
    setActiveTab(tabName);
  };

    // Set canvas dimensions when video metadata is loaded
    const handleMetadataLoaded = () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    };
  

  const renderTabContent = () => {
    switch (activeTab) {

      case 'Camera':
        return (
          <div>
            <Webcam height={1080} audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                ...videoConstraints,
                facingMode
              }} />
            <button onClick={handleSwitch} type="button" className="my-4 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
              Switch camera</button>
              <p className='text-md  text-gray-500'> detected speed {speed}</p>

          </div>



        );

      case 'Video':
        return (
          <div>

            <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="file_input">Upload file</label>
            <input onChange={handleVideoFileChange} class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="file_input" type="file" />

            <button onClick={handlePlayClick} type="button" className="my-4 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
              Start Video</button>
            <video ref={videoRef} width="1920" height="1080" onLoadedMetadata={handleMetadataLoaded}/>
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <div className='flex flex-col'>
              <h3 className='text-white text-2xl font-bold my-4'>Last captured frame</h3>
         
            </div>
          </div>
        );
      // Add cases for other tabs as needed
      default:
        return null;


    }
  };

  const handleVideoFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const videoURL = URL.createObjectURL(file);
      videoRef.current.src = videoURL;
    }
  };

  const handlePlayClick = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const interval = 500; // 1 second

    const captureScreenshot = async () => {
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, video.width, video.height);
      const screenshotData = canvas.toDataURL('image/png');
      const blob = await fetch(screenshotData).then((res) => res.blob());

      sendPhoto(blob);
      setScreenshots((prevScreenshots) => [...prevScreenshots, screenshotData]);
    };

    video.play();
    const screenshotInterval = setInterval(captureScreenshot, interval);

    video.addEventListener('ended', () => {
      clearInterval(screenshotInterval);
    });
  };

  
  // const captureVideoScreenshot = (screenshotData) => {

  // }




  const startInterval = () => {
    setIsCameraOn(true);
    const id = setInterval(captureWebcamScreenshot, 500);
    setIntervalId(id);
  };

  const stopInterval = () => {
    setIsCameraOn(false);
    clearInterval(intervalId);
    setIntervalId(null);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFileName(file.name);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
    setSelectedFile(file);
  };

  const showNewSpeed = (newSpeed) => {
    if (newSpeed !== 0) {
      setSpeed(newSpeed);
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
          showNewSpeed(data)
        })
        .catch(error => {
          console.error('Error during upload', error);
        });
    }
  };


  const captureWebcamScreenshot = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    const blob = await fetch(imageSrc).then((res) => res.blob());
    const webCamSpeed = sendPhoto(blob);
    setWebCamSpeed(webCamSpeed);
  }, [webcamRef]);

  const sendPhoto = (photo) => {
    const formData = new FormData();
    formData.append('photo', photo);

    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        showNewSpeed(data)
        setLastSpeedPredictions((prevSpeedPredictions) => [...prevSpeedPredictions, data]);
        setLastChangeAt(Date.now());
        setChangingSpeed(true);
      })
      .catch(error => {
        console.error('Error during upload', error);
      });
  }


  useEffect(() => {
    if (lastChangeAt !== null) {
      const interval = setInterval(() => {
        if(!changingSpeed) return;
        
        if (Date.now() - lastChangeAt > 3000) {
          // get the most repeated speed other than 0 in lastSpeedPredictions array
          const mostRepeatedSpeed = lastSpeedPredictions.filter(speed => speed !== 0).reduce((a, b, i, arr) =>
            (arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b), null);

          
          console.log("mostRepeatedSpeed", mostRepeatedSpeed);
          setMostRepeatedSpeed(mostRepeatedSpeed);
          setChangingSpeed(false);

          
          setLastSpeedPredictions([]);
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  });
  

  const handleSwitch = React.useCallback(() => {
    setFacingMode(
      prevState =>
        prevState === FACING_MODE_USER
          ? FACING_MODE_ENVIRONMENT
          : FACING_MODE_USER
    );
  }, []);



  return (
    <div className="">
      <section className="bg-white dark:bg-gray-900 h-screen ">
        <div className="grid max-w-screen-xl px-4 py-8 mx-auto lg:gap-8 xl:gap-0 lg:py-16 lg:grid-cols-12">
          <div className="py-8 px-4 mx-auto max-w-screen-xl text-center lg:py-16 lg:px-12 mr-auto place-self-center lg:col-span-7">

            <h1 className="mb-4 text-4xl font-extrabold tracking-tight leading-none text-gray-900 md:text-5xl lg:text-6xl dark:text-white">Haddy 34an T3dy</h1>
            <h1 className="mb-8 text-3xl font-bold tracking-tight leading-none text-gray-900  dark:text-gray-400">🚗هـــــــدّي عشـــــــــان تعــــــــــدي 🚗 </h1>


            <div className="container justify-center flex">
              <div className="md:flex">
                <ul className="flex-column space-y space-y-4 text-sm font-medium text-gray-500 dark:text-gray-400 md:me-4 mb-4 md:mb-0">
                  <li>
                    <a
                      href="#"
                      className={`inline-flex items-center px-4 py-3 text-white bg-blue-700 rounded-lg w-full dark:bg-blue-600 ${activeTab === 'profile' && 'active'}`}
                      onClick={() => handleTabClick('Camera')}
                    >
                      Camera
                    </a>
                  </li>
                  <li>

                    <a
                      href="#"
                      className={`inline-flex items-center px-4 py-3 text-white bg-blue-700 rounded-lg w-full dark:bg-blue-600 ${activeTab === 'settings' && 'active'}`}
                      onClick={() => handleTabClick('Video')}
                    >

                      Video
                    </a>
                  </li>
                </ul>
                {renderTabContent()}
              </div>

            </div>

            <div>
            </div>

          </div>
          <div className="mt-0 col-span-5 ">

            <div className=" mb-8 lg:mb-16   ">

              <div class="flex items-center justify-center w-full">
                <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                  <div class="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg class="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
                    </svg>
                    <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF (MAX. 800x400px)</p>
                  </div>
                  <input onChange={handleFileChange} id="dropzone-file" type="file" class="hidden" />
                </label>
              </div>
              {/* <p className="text-xs text-gray-500 dark:text-gray-400">
            {selectedFileName || "SVG, PNG, JPG or GIF (MAX. 800x400px)"}
          </p> */}
              <button disabled={selectedFile ? false : true} onClick={handleUpload} type="button" className="my-4 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
                Upload Photo</button>
              <button onClick={() => {
                setImagePreview(null);
                setSelectedFile(null);
                setSelectedFileName("");
              }} type="button" className="my-4 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
                Remove Picture</button>
              {imagePreview ? (
                <img
                  src={imagePreview}
                  alt="Selected preview"
                  className="mb-4  object-cover h-48 my-4"
                />
              ) : (
                null
              )}

            </div>
            <div>
              <h1 className='text-white text-4xl font-bold my-4'>Current Speed Is <span className='text-6xl font-extrabold text-green-500'>{mostRepeatedSpeed}</span></h1>
              <p className='text-md  text-gray-500'> detected speed {speed}</p>

            </div>
            <div>
              <button onClick={captureWebcamScreenshot} type="button" className="text-white mt-10 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2  dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
                Capture Photo</button>
                <button onClick={startInterval} type="button" className="text-white mt-10 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2  dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
                Start Camera</button>
                <button onClick={stopInterval} type="button" className="text-white mb-2 mt-10 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2  dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
                Stop Camera</button>
                




            </div>
            <div>
            <p className='
            text-md  text-gray-400'>{
              isCameraOn ? "Camera is on" : "Camera is off"
            }</p>
            {screenshots.length > 0 && (
                <img
                  src={screenshots[screenshots.length - 1]}
                  alt="Screenshot"
                  width={300}
                />
              )}
            </div>
          </div>
        </div>

      </section>
    </div>
  );
}

export default App;
