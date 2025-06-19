// mushi-frontend/src/components/categorycard/CategoryCard.jsx
import React, { useCallback, useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faClosedCaptioning,
  faMicrophone,
  faPlay,
} from "@fortawesome/free-solid-svg-icons";
import { FaChevronRight } from "react-icons/fa";
import "./CategoryCard.css";
import { useLanguage } from "@/context/LanguageContext";
import { Link, useNavigate } from "react-router-dom";

const CategoryCard = React.memo(
  ({
    label,
    data,
    showViewMore = true,
    className,
    categoryPage = false,
    cardStyle,
    path,
    limit,
    cardRefs, // Receives the refs object
    onMouseEnter,
    onMouseLeave,
  }) => {
    const { language } = useLanguage();
    const navigate = useNavigate();

    if (limit) {
      data = data.slice(0, limit);
    }

    const [itemsToRender, setItemsToRender] = useState({
      firstRow: [],
      remainingItems: [],
    });

    const getItemsToRender = useCallback(() => {
      if (categoryPage) {
        const firstRow =
          window.innerWidth > 758 && data.length > 4 ? data.slice(0, 4) : [];
        const remainingItems =
          window.innerWidth > 758 && data.length > 4
            ? data.slice(4)
            : data.slice(0);
        return { firstRow, remainingItems };
      }
      return { firstRow: [], remainingItems: data.slice(0) };
    }, [categoryPage, data]);

    useEffect(() => {
      const handleResize = () => setItemsToRender(getItemsToRender());
      handleResize();
      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    }, [getItemsToRender]);

    const renderCardDetails = (item) => {
      const type = item.show_type || item.tvInfo?.showType;
      const duration = item.duration || item.tvInfo?.duration;
      const cleanDuration = duration && duration !== 'm' && duration !== '?' ? duration : null;

      if (!type && !cleanDuration) return null;

      return (
        <div className="flex items-center gap-x-2 w-full mt-2 overflow-hidden text-gray-400 text-sm">
          {type && <div className="text-nowrap overflow-hidden text-ellipsis capitalize">{type.split(" ").shift()}</div>}
          {type && cleanDuration && <div className="dot"></div>}
          {cleanDuration && <div className="text-nowrap overflow-hidden text-ellipsis">{cleanDuration}</div>}
        </div>
      );
    };

    const renderCard = (item, isFirstRow) => {
      const imageHeightClass = isFirstRow
        ? 'h-[320px] max-[1200px]:h-[35vw] max-[758px]:h-[45vw] max-[478px]:h-[60vw] ultra-wide:h-[400px]'
        : 'h-[250px] max-[1200px]:h-[35vw] max-[758px]:h-[45vw] max-[478px]:h-[60vw]';

      return (
        <div
          key={item.id}
          className="flex flex-col transition-transform duration-300 ease-in-out h-fit"
          ref={(el) => (cardRefs.current[item.id] = el)}
          onMouseEnter={() => onMouseEnter(item.id, cardRefs.current[item.id])}
          onMouseLeave={onMouseLeave}
        >
          <div
            className="w-full relative group hover:cursor-pointer"
            onClick={() => navigate(`/anime/details/${item.id}`)}
          >
            <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors z-[1] flex items-center justify-center">
                <FontAwesomeIcon icon={faPlay} className="text-4xl text-white opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="overlay"></div>
            <div className="overflow-hidden">
              <img
                src={`https://wsrv.nl/?url=${item.poster_url || item.poster}`}
                alt={item.title}
                className={`w-full object-cover transform transition-all duration-300 ease-in-out ${imageHeightClass} ${cardStyle}`}
              />
            </div>
            {(item.tvInfo?.rating === "18+" || item?.adultContent === true) && (
              <div className="text-white px-2 rounded-md bg-[#FF5700] absolute top-2 left-2 flex items-center justify-center text-[14px] font-bold z-10">18+</div>
            )}
            <div className="absolute left-2 bottom-4 flex items-center justify-center w-fit space-x-1 z-[100] max-[270px]:flex-col max-[270px]:gap-y-[3px]">
              {item.tvInfo?.sub && (
                <div className="flex space-x-1 justify-center items-center bg-[#B0E3AF] rounded-[2px] px-[4px] text-black py-[2px]">
                  <FontAwesomeIcon icon={faClosedCaptioning} className="text-[12px]" />
                  <p className="text-[12px] font-bold">{item.tvInfo.sub}</p>
                </div>
              )}
              {item.tvInfo?.dub && (
                <div className="flex space-x-1 justify-center items-center bg-[#B9E7FF] rounded-[2px] px-[8px] text-black py-[2px]">
                  <FontAwesomeIcon icon={faMicrophone} className="text-[12px]" />
                  <p className="text-[12px] font-bold">{item.tvInfo.dub}</p>
                </div>
              )}
            </div>
          </div>
          <Link
            to={`/anime/details/${item.id}`}
            className="text-white font-semibold mt-1 item-title hover:text-[#FFBADE] hover:cursor-pointer line-clamp-1"
          >
            {language === "EN" ? item.title : (item.jname || item.japanese_title)}
          </Link>
          {isFirstRow && item.description && (
            <div className="line-clamp-3 text-[13px] font-extralight text-[#b1b0b0] max-[1200px]:hidden">{item.description}</div>
          )}
          {renderCardDetails(item)}
        </div>
      );
    };

    return (
      <div className={`w-full ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h1 className="font-bold text-2xl text-[#ffbade] max-[478px]:text-[18px] capitalize">{label}</h1>
          {showViewMore && (
            <Link to={path ? `/search?category=${path}&title=${encodeURIComponent(label)}` : '#'} className="flex w-fit items-baseline h-fit rounded-3xl gap-x-1 group">
              <p className="text-white text-[12px] font-semibold h-fit leading-0 group-hover:text-[#ffbade] transition-all ease-out">View more</p>
              <FaChevronRight className="text-white text-[10px] group-hover:text-[#ffbade] transition-all ease-out" />
            </Link>
          )}
        </div>
        <>
          {categoryPage && (
            <div className={`grid grid-cols-4 gap-x-3 gap-y-8 transition-all duration-300 ease-in-out ${categoryPage && itemsToRender.firstRow.length > 0 ? "mt-8 max-[758px]:hidden" : ""}`}>
              {itemsToRender.firstRow.map((item) => renderCard(item, true))}
            </div>
          )}
          <div className="grid grid-cols-6 gap-x-3 gap-y-8 mt-6 transition-all duration-300 ease-in-out max-[1400px]:grid-cols-4 max-[758px]:grid-cols-3 max-[478px]:grid-cols-2">
            {itemsToRender.remainingItems.map((item) => renderCard(item, false))}
          </div>
        </>
      </div>
    );
  }
);

CategoryCard.displayName = "CategoryCard";

export default CategoryCard;
