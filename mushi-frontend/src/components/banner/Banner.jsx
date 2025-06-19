// mushi-frontend/src/components/banner/Banner.jsx
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPlay,
  faCalendar,
  faClock,
} from "@fortawesome/free-solid-svg-icons";
import { FaChevronRight } from "react-icons/fa";
import { Link } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";
import "./Banner.css";

function Banner({ item, index, isActive }) {
  const { language } = useLanguage();

  if (!item) return null;

  return (
    // --- START OF FIX: The component no longer renders its own image ---
    // The main section is now just a container for the overlay elements
    <section className="spotlight w-full h-full relative">
      <div className="spotlight-overlay"></div>

      <div
        className={`absolute flex flex-col left-0 bottom-[50px] w-[55%] p-4 z-10 max-[1390px]:w-[45%] max-[1390px]:bottom-[10px] max-[1300px]:w-[600px] max-[1120px]:w-[60%] max-md:w-[90%] max-[300px]:w-full transition-all duration-500 ease-out ${isActive ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}
      >
        <p className="text-[#ffbade] font-semibold text-[20px] w-fit max-[1300px]:text-[15px]">
          #{index + 1} Spotlight
        </p>
        <h3 className="text-white line-clamp-2 text-5xl font-bold mt-6 text-left max-[1390px]:text-[45px] max-[1300px]:text-3xl max-[1300px]:mt-4 max-md:text-2xl max-md:mt-1 max-[575px]:text-[22px] max-sm:leading-6 max-sm:w-[80%] max-[320px]:w-full ">
          {language === "EN" ? item.title : (item.japanese_title || item.title)}
        </h3>
        <div className="flex h-fit justify-start items-center flex-wrap w-full gap-x-5 gap-y-2 mt-8 max-[1300px]:mt-6 max-md:hidden">
          {item.tvInfo?.showType && (
            <div className="flex space-x-2 justify-center items-center">
              <FontAwesomeIcon icon={faPlay} className="text-[12px] bg-white text-black p-1 rounded-full" />
              <p className="text-white text-base">{item.tvInfo.showType}</p>
            </div>
          )}

          {item.tvInfo?.duration && (
            <div className="flex space-x-2 justify-center items-center">
              <FontAwesomeIcon icon={faClock} className="text-white text-sm" />
              <p className="text-white text-base">{item.tvInfo.duration}</p>
            </div>
          )}

          {item.tvInfo?.releaseDate && (
            <div className="flex space-x-2 justify-center items-center">
              <FontAwesomeIcon icon={faCalendar} className="text-white text-sm" />
              <p className="text-white text-base">{item.tvInfo.releaseDate}</p>
            </div>
          )}

          {item.tvInfo?.quality && (
            <div className="bg-[#ffbade] py-[2px] px-2 rounded text-black text-xs font-bold h-fit">
              {item.tvInfo.quality}
            </div>
          )}
        </div>
        <p className="text-white text-[17px] font-sm mt-6 text-left line-clamp-3 max-[1200px]:line-clamp-2 max-[1300px]:w-[500px] max-[1120px]:w-[90%] max-md:hidden">
          {item.description}
        </p>
        <div className="flex gap-x-5 mt-10 max-md:mt-6 max-sm:w-full max-[320px]:flex-col max-[320px]:space-y-3">
          <Link
            to={`/watch/${item.id}`}
            className="flex justify-center items-center bg-[#ffbade] px-4 py-2 rounded-3xl gap-x-2 text-black max-[320px]:w-fit"
          >
            <FontAwesomeIcon icon={faPlay} className="text-xs" />
            <span className="max-[1000px]:text-[15px] font-semibold max-[320px]:text-[12px]">
              Watch Now
            </span>
          </Link>
          <Link
            to={`/anime/details/${item.id}`}
            className="flex bg-[#3B3A52] justify-center items-center px-4 py-2 rounded-3xl gap-x-2 max-[320px]:w-fit max-[320px]:px-3"
          >
            <p className="text-white max-[1000px]:text-[15px] font-semibold max-[320px]:text-[12px]">
              Detail
            </p>
            <FaChevronRight className="text-white max-[320px]:text-[10px]" />
          </Link>
        </div>
      </div>
    </section>
     // --- END OF FIX ---
  );
}

export default Banner;
