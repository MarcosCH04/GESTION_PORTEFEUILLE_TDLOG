// frontend/src/components/Spinner.jsx
import React from "react";

function Spinner({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Spinner animation */}
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 rounded-full"></div>
        <div className="w-16 h-16 border-4 border-primary-500 rounded-full border-t-transparent animate-spin absolute top-0 left-0"></div>
      </div>
      
      {/* Loading Message */}
      <p className="mt-4 text-gray-600 font-medium">{message}</p>
    </div>
  );
}

export default Spinner;