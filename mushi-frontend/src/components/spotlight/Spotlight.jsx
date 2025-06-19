// mushi-frontend/src/components/spotlight/Spotlight.jsx
import React, { useState, useEffect } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { EffectCoverflow, Pagination, Navigation, Autoplay } from "swiper/modules";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlay, faCalendar, faClock } from "@fortawesome/free-solid-svg-icons";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import { Link } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";

// Import Swiper and local styles
import "swiper/css";
import "swiper/css/effect-coverflow";
import "swiper/css/pagination";
import "swiper/css/navigation";
import "./Spotlight.css";

// Snail rotation logic
const snailImages = [
  '/mushi_snail_luffy.png', '/mushi_snail_zoro.png', '/mushi_snail_nami.png',
  '/mushi_snail_usopp.png', '/mushi_snail_sanji.png', '/mushi_snail_chopper.png',
  '/mushi_snail_robin.png', '/mushi_snail_franky.png', '/mushi_snail_brook.png',
  '/mushi_snail_ace.png', '/mushi_snail_sabo.png'
];

const useRotatingSnail = () => {
    const [currentSnailIndex, setCurrentSnailIndex] = useState(0);
    useEffect(() => {
        const intervalId = setInterval(() => {
            setCurrentSnailIndex(prevIndex => (prevIndex + 1) % snailImages.length);
        }, 15000);
        return () => clearInterval(intervalId);
    }, []);
    return snailImages[currentSnailIndex];
};

const Spotlight = ({ spotlights }) => {
  const { language } = useLanguage();
  const currentSnailImage = useRotatingSnail();

  // --- START OF FIX: Add a filter to remove any null/undefined items from the array ---
  const validSpotlights = spotlights ? spotlights.filter(item => item && item.poster_url) : [];
  // --- END OF FIX ---

  return (
    <div className="relative h-[600px] max-[1390px]:h-[530px] max-[1300px]:h-[500px] max-md:h-[420px] spotlight-container">

        {/* --- START OF FIX: Check validSpotlights instead of spotlights --- */}
        {validSpotlights && validSpotlights.length > 0 ? (
        // --- END OF FIX ---
          <>
            <Swiper
              effect={'coverflow'}
              grabCursor={true}
              centeredSlides={true}
              slidesPerView={'auto'}
              loop={true}
              coverflowEffect={{
                rotate: 50,
                stretch: 0,
                depth: 100,
                modifier: 1,
                slideShadows: true,
              }}
              autoplay={{
                delay: 5000,
                disableOnInteraction: false,
              }}
              pagination={{ clickable: true }}
              navigation={{
                nextEl: ".button-next",
                prevEl: ".button-prev",
              }}
              modules={[EffectCoverflow, Pagination, Navigation, Autoplay]}
              className="spotlight-swiper"
            >
              {/* --- START OF FIX: Map over validSpotlights --- */}
              {validSpotlights.map((item, index) => (
                <SwiperSlide
                  key={item.id || index}
                  className="spotlight-slide"
                  // Use a fallback for the background image to prevent errors
                  style={{ backgroundImage: `url(https://wsrv.nl/?url=${item.poster_url || ''})` }}
                >
              {/* --- END OF FIX --- */}
                  <div className="spotlight-overlay-simple"></div>

                  <div className="banner-content-container">
                    <p className="text-[#ffbade] font-semibold text-xl [text-shadow:0_2px_5px_rgba(0,0,0,0.8)]">
                      #{index + 1} Spotlight
                    </p>

                    <h3 className="text-white line-clamp-2 text-5xl font-bold mt-4 text-left [text-shadow:0_2px_8px_rgba(0,0,0,0.8)] max-[1390px]:text-[45px] max-[1300px]:text-4xl max-md:text-3xl">
                      {language === "EN" ? item.title : (item.jname || item.title)}
                    </h3>

                    <div className="flex h-fit justify-start items-center flex-wrap w-full gap-x-5 gap-y-2 mt-6 max-md:hidden [text-shadow:0_2px_4px_rgba(0,0,0,0.8)]">
                      {item.tvInfo?.showType && (
                        <div className="flex space-x-2 justify-center items-center">
                          <FontAwesomeIcon icon={faPlay} className="text-xs bg-white text-black p-1 rounded-full" />
                          <p className="text-white text-base">{item.tvInfo.showType}</p>
                        </div>
                      )}
                      {item.tvInfo?.duration && (
                        <div className="flex space-x-2 justify-center items-center">
                          <FontAwesomeIcon icon={faClock} className="text-white text-sm" />
                          <p className="text-white text-base">{item.tvInfo.duration}</p>
                        </div>
                      )}
                    </div>

                    <p className="text-white text-base mt-6 text-left line-clamp-3 [text-shadow:0_1px_6px_rgba(0,0,0,0.9)] max-[1200px]:line-clamp-2 max-[1300px]:w-[550px] max-[1120px]:w-[90%] max-md:hidden">
                      {item.description}
                    </p>

                    <div className="flex gap-x-5 mt-8 max-md:mt-6">
                      <Link
                        to={`/watch/${item.id}`}
                        className="flex justify-center items-center bg-[#ffbade] px-5 py-2.5 rounded-full gap-x-2 text-black font-semibold hover:scale-105 transition-transform"
                      >
                        <FontAwesomeIcon icon={faPlay} className="text-sm" />
                        <span>Watch Now</span>
                      </Link>
                      <Link
                        to={`/anime/details/${item.id}`}
                        className="flex bg-white/20 backdrop-blur-md justify-center items-center px-5 py-2.5 rounded-full gap-x-2 text-white font-semibold hover:bg-white/30 transition-colors"
                      >
                        <span>Details</span>
                        <FaChevronRight className="text-sm" />
                      </Link>
                    </div>
                  </div>
                </SwiperSlide>
              ))}
            </Swiper>

            <div className="button-prev">
                <FaChevronLeft size={18} />
                <img src={currentSnailImage} alt="Previous" className="mushi-nav-icon" />
            </div>
            <div className="button-next">
                <img src={currentSnailImage} alt="Next" className="mushi-nav-icon" />
                <FaChevronRight size={18} />
            </div>
          </>
        ) : (
          <p className="text-white text-center">No spotlights to show.</p>
        )}
      </div>
  );
};

export default Spotlight;
