// mushi-frontend/src/components/navigation/FooterNav.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function FooterNav({ images, currentIndex }) {
  const websiteName = "Clank Clank Mushi";

  return (
    <footer className="relative flex flex-col w-full mt-[100px] px-4 overflow-hidden">
      {/* KEPT (from Mushi): The signature background image carousel for the footer */}
      <img
        src={images[currentIndex]}
        alt={`Footer background image ${currentIndex + 1}`}
        className="absolute inset-0 w-full h-full object-cover transition-opacity duration-1000"
        style={{ opacity: 0.05 }} // Very subtle opacity for a footer
      />
      {/* KEPT (from Mushi): Overlay to ensure text readability */}
      <div className="absolute inset-0 bg-purple-900 opacity-65 z-0"></div>

      <div className="relative z-10 py-5 flex flex-col w-full space-y-4 max-md:items-center">
        {/* Feature: A-Z List (from Zenime), now using theme colors */}
        <div className="flex w-fit items-center space-x-6 max-[500px]:hidden">
          <p className="text-2xl font-bold max-md:text-lg text-foreground/90">A-Z LIST</p>
          <p style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.4)' }} className="text-md font-semibold pl-6 text-foreground/70">
            Searching anime order by alphabet name A to Z
          </p>
        </div>
        <div className="flex gap-x-[7px] flex-wrap justify-start gap-y-2 max-md:justify-start max-[500px]:hidden">
          {[ "All", "#", "0-9", ...Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i))].map((item) => (
            <Link
              to={`/az-list/${item === "All" ? "" : item}`} // You'll need to create this route
              key={item}
              className="text-lg bg-secondary/80 text-muted-foreground px-2 rounded-md font-bold hover:text-black hover:bg-[#FFBADE] hover:cursor-pointer transition-all ease-out"
            >
              {item}
            </Link>
          ))}
        </div>

        {/* Feature: Disclaimer and Copyright (from Zenime), now using theme colors */}
        <div className="flex flex-col w-full text-left space-y-2 pt-4 max-md:items-center max-[470px]:px-[5px]">
          <p className="text-muted-foreground text-[15px] max-md:text-center max-md:text-[12px]">
            {websiteName} does not host any files, it merely pulls streams from 3rd party services.
            Legal issues should be taken up with the file hosts and providers. {websiteName} is not responsible for any media files shown.
          </p>
          <p className="text-muted-foreground max-md:text-[14px]">
            Powered by the Mushi LLM | © {new Date().getFullYear()} {websiteName}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default FooterNav;
