// frontend/src/main.jsx
/** This is the React Application Entry Point
 * The file initializes the React application by rendering te root component (App) 
 * and mounts it to the DOM element with the ID 'root'
 * It's the bridge between the HTML file and the React components
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

/**
 * Mount the React app to the DOM (Document Object Model)
 * Finds the <div id="root"> in the HTML and renders te App component inside it 
 * The StrictMode enables additional checks and warnings 
 */

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
