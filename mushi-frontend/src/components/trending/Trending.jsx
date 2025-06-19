// mushi-frontend/src/components/trending/Trending.jsx
import React, { useState, useEffect } from "react";
import { Pagination, Navigation } from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import { useLanguage } from "@/context/LanguageContext";
import { Link, useNavigate } from "react-router-dom";

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


const Trending = ({ trending }) => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const currentSnailImage = useRotatingSnail();

  return (
    <div className="w-full">
      <div className="relative mx-auto overflow-hidden z-[1] max-[759px]:pr-0">
        <Swiper
          className="w-full h-full"
          slidesPerView={2}
          spaceBetween={15}
          breakpoints={{
            479: { slidesPerView: 3, spaceBetween: 15 },
            640: { slidesPerView: 3, spaceBetween: 15 },
            900: { slidesPerView: 4, spaceBetween: 15 },
            1300: { slidesPerView: 6, spaceBetween: 15 },
          }}
          modules={[Pagination, Navigation]}
          navigation={{
            nextEl: ".trending-button-next",
            prevEl: ".trending-button-prev",
          }}
        >
          {trending &&
            trending.map((item, idx) => (
              <SwiperSlide
                key={item.id || idx}
                className="text-center flex text-[18px] justify-center items-center cursor-pointer"
                onClick={() => navigate(`/anime/details/${item.id}`)}
              >
                <div className="w-full h-auto pb-[135%] relative inline-block overflow-hidden max-[575px]:pb-[150%] group">
                  <div className="absolute left-0 top-0 bottom-0 overflow-hidden w-[40px] text-center font-semibold bg-[#201F31] max-[575px]:top-0 max-[575px]:h-[30px] max-[575px]:z-[9] max-[575px]:bg-white">
                    <span className="absolute left-0 right-0 bottom-0 text-[24px] leading-[1.1em] text-center z-[9] transform -rotate-90 text-white/50 group-hover:text-white transition-colors max-[575px]:transform max-[575px]:rotate-0 max-[575px]:text-[#111] max-[575px]:text-[18px] max-[575px]:leading-[30px]">
                      {item.number || idx + 1}
                    </span>
                  </div>
                  <Link
                    to={`/anime/details/${item.id}`}
                    className="inline-block bg-[#2a2c31] absolute w-auto left-[40px] right-0 top-0 bottom-0 max-[575px]:left-0 max-[575px]:top-0 max-[575px]:bottom-0"
                  >
                    <img
                      src={`https://wsrv.nl/?url=${item.poster_url || item.poster}`}
                      alt={item.title}
                      className="block w-full h-full object-cover transition-transform group-hover:scale-110"
                      title={item.title}
                    />
                  </Link>
                </div>
              </SwiperSlide>
            ))}
        </Swiper>

        <div className="absolute -right-5 -left-5 top-1/2 -translate-y-1/2 flex items-center justify-between z-20 max-[759px]:hidden">
            <div className="trending-button-prev w-[90px] h-[48px] text-white bg-black/40 backdrop-blur-sm border border-white/10 rounded-full flex justify-center items-center cursor-pointer transition-all duration-300 shadow-lg gap-1.5 p-3 hover:bg-[#ffbade] hover:text-black hover:scale-105">
                <FaChevronLeft size={16} />
                <img src={currentSnailImage} alt="Previous" className="mushi-nav-icon" />
            </div>
            <div className="trending-button-next w-[90px] h-[48px] text-white bg-black/40 backdrop-blur-sm border border-white/10 rounded-full flex justify-center items-center cursor-pointer transition-all duration-300 shadow-lg gap-1.5 p-3 hover:bg-[#ffbade] hover:text-black hover:scale-105">
                <img src={currentSnailImage} alt="Next" className="mushi-nav-icon" />
                <FaChevronRight size={16} />
            </div>
        </div>
      </div>
    </div>
  );
};

export default Trending;
